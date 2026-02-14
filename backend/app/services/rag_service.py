from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

from app.core.config import settings
from app.models.rag_models import DocumentChunk, ChatMessage


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings_model = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=settings.OLLAMA_BASE_URL
        )
        self.llm = ChatOllama(
            model="phi3",
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.1
        )

    async def get_history(self, session_id: str, limit: int = 6):
        stmt = select(ChatMessage).where(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(limit)

        result = await self.db.execute(stmt)
        msgs = result.scalars().all()
        return msgs[::-1]

    async def save_message(self, session_id: str, role: str, content: str):
        msg = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(msg)
        await self.db.commit()

    async def contextualize_question(self, question: str, history_msgs):
        if not history_msgs:
            return question

        chat_history = []
        for msg in history_msgs:
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            else:
                chat_history.append(AIMessage(content=msg.content))

        system_prompt = """
        Você é uma ferramenta técnica de reescrita de consultas para banco de dados vetorial.
        Sua ÚNICA função é reformular a pergunta do usuário para torná-la independente, baseada no histórico.
        
        REGRAS RIGÍDAS:
        1. NÃO responda à pergunta.
        2. NÃO dê dicas, receitas ou explicações.
        3. Apenas retorne a pergunta reformulada em uma única frase.
        4. Se a pergunta já for clara, retorne ela exatamente igual.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        new_question = chain.invoke({
            "chat_history": chat_history,
            "question": question
        })
        new_question = new_question.strip().split('\n')[-1]

#rets

        print(f"Pergunta Original: {question} | Reespectiva: {new_question}")
        return new_question

    async def buscar_contexto(self, pergunta_vetor: str, limite: int = 8, limiar_corte: float = 0.88):

        vetor_pergunta = self.embeddings_model.embed_query(pergunta_vetor)

        distancia = DocumentChunk.embedding.l2_distance(vetor_pergunta)
        stmt = select(DocumentChunk, distancia).order_by(
            distancia).limit(limite)

        resultado = await self.db.execute(stmt)
        rows = resultado.all()

        chunks_validos = []
        for row in rows:
            chunk = row[0]
            score = row[1]

            if score < limiar_corte:
                print(
                    f"✅ Match aceito: {score:.4f} | Texto: {chunk.content[:50]}...")
                chunks_validos.append(chunk.content)
            else:
                print(
                    f"Lixo descartado (muito longe): {score:.4f} | Texto: {chunk.content[:50]}...")

        return list(set(chunks_validos))

    async def responder(self, pergunta: str, session_id: str):

        historico_db = await self.get_history(session_id)

        pergunta_search = await self.contextualize_question(pergunta, historico_db)

        contextos = await self.buscar_contexto(pergunta_search)

        if not contextos:
            return {"resposta": "Não encontrei informações nos documentos.", "fontes": []}

        texto_contexto = "\n\n---\n\n".join(contextos)

        template = """
        Você é o Synca, um assistente corporativo preciso.
        
        INSTRUÇÕES ESTRITAS:
        1. Use APENAS as informações contidas no CONTEXTO abaixo para responder.
        2. O CONTEXTO pode conter informações irrelevantes (ruído). IGNORE trechos que não tenham relação direta com a PERGUNTA.
        3. Se a resposta não estiver no contexto, diga: "Não tenho informações suficientes nesse documento."
        4. NÃO invente informações. NÃO use conhecimento externo.
        5. Responda de forma direta e técnica.

        CONTEXTO:
        {contexto}

        PERGUNTA DO USUÁRIO: 
        {pergunta}
        """
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm | StrOutputParser()

        resposta = chain.invoke({
            "contexto": texto_contexto,
            "pergunta": pergunta
        })

        await self.save_message(session_id, "user", pergunta)
        await self.save_message(session_id, "assistant", resposta)

        return {
            "resposta": resposta,
            "fontes_utilizadas": contextos
        }
