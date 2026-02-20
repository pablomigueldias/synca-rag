from sqlalchemy.ext.asyncio import AsyncSession  # type: ignore
from sqlalchemy import select  # type: ignore
from langchain_ollama import OllamaEmbeddings, ChatOllama  # type: ignore
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder  # type: ignore
from langchain_core.output_parsers import StrOutputParser  # type: ignore
from langchain_core.messages import HumanMessage, AIMessage  # type: ignore
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.tools import tool
from langchain_classic import hub

from app.core.config import settings
from app.models.rag_models import DocumentChunk, ChatMessage
from app.services.tools import pesquisar_internet


class RAGService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings_model = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=settings.OLLAMA_BASE_URL
        )
        self.llm = ChatOllama(
            model="llama3.1",
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
        Você é uma API de reescrita de buscas. Sua ÚNICA função é retornar a pergunta original reformulada considerando o histórico.
        NÃO seja educado. NÃO responda à pergunta. NÃO adicione explicações. Retorne APENAS a string de busca.
        
        EXEMPLOS:
        Histórico: O que é Docker?
        Pergunta: E como eu instalo ele?
        Saída: Como instalar o Docker?
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

        chain = prompt | self.llm | StrOutputParser()

        new_question = await chain.ainvoke({
            "chat_history": chat_history,
            "question": question
        })

        new_question = new_question.strip().split('\n')[-1]

        print(f"Pergunta Original: {question} | Reespectiva: {new_question}")
        return new_question

    async def buscar_contexto(self, pergunta_vetor: str, limite: int = 8, limiar_corte: float = 0.50):
        query_otimizada = f"search_query: {pergunta_vetor}"
        vetor_pergunta = self.embeddings_model.embed_query(query_otimizada)

        distancia = DocumentChunk.embedding.cosine_distance(vetor_pergunta)

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
                    f"✅ Match (Cosseno): {score:.4f} | Texto: {chunk.content[:50]}...")
                chunks_validos.append(chunk.content)
            else:
                print(
                    f"🗑️ Descartado (Cosseno): {score:.4f} | Texto: {chunk.content[:50]}...")

        return list(set(chunks_validos))

    async def responder(self, pergunta: str, session_id: str):
        print(f"⚡ [Synca] Nova missão recebida: {pergunta}")

        historico_db = await self.get_history(session_id)
        chat_history = []
        for msg in historico_db:
            if msg.role == "user":
                chat_history.append(HumanMessage(content=msg.content))
            else:
                chat_history.append(AIMessage(content=msg.content))

        ferramentas = self.obter_ferramentas()

        prompt_react = hub.pull("hwchase17/react-chat")

        instrucoes_iniciais = """Você é o Synca, a IA oficial e Assistente Executivo.
        Sua missão é ajudar o usuário respondendo de forma técnica, precisa e direta.
        
        REGRAS DE OURO:
        1. Se a pergunta for sobre Pablo Ortiz, seus projetos, habilidades ou currículo, USE OBRIGATORIAMENTE a ferramenta 'pesquisar_documentos_internos'.
        2. Se a pergunta for sobre notícias, cotações, ou conhecimentos gerais que você não saiba, USE A FERRAMENTA 'pesquisar_internet'.
        
        REGRA CRÍTICA DE SAÍDA:
        Quando você souber a resposta final, encerre IMEDIATAMENTE usando o prefixo exato "Final Answer:". 
        NUNCA use negrito como "**Final Answer**". NUNCA traduza para "Resposta Final". Apenas digite "Final Answer: " seguido da sua resposta em Markdown.
        \n"""

        prompt_react.template = instrucoes_iniciais + prompt_react.template


        agente = create_react_agent(self.llm, ferramentas, prompt_react)

        agent_executor = AgentExecutor(
            agent=agente,
            tools=ferramentas,
            verbose=True,
            max_iterations=4,
            handle_parsing_errors="Formato inválido. Apenas me dê a resposta final começando com 'Final Answer: '"
        )

        try:
            resposta_agente = await agent_executor.ainvoke({
                "input": pergunta,
                "chat_history": chat_history
            })

            resposta_final = resposta_agente["output"]

        except Exception as e:
            print(f"❌ Erro crítico no motor do Agente: {str(e)}")
            resposta_final = "Desculpe, meu processamento neural encontrou um erro ao tentar usar as ferramentas."

        await self.save_message(session_id, "user", pergunta)
        await self.save_message(session_id, "assistant", resposta_final)

        return {
            "resposta": resposta_final,
            "fontes_utilizadas": ["Memória RAG", "Internet"]
        }

    def obter_ferramentas(self):
        """
        Fábrica de Ferramentas: Une ferramentas externas (Internet) 
        com ferramentas internas que precisam do Banco de Dados (RAG).
        """

        @tool
        async def pesquisar_documentos_internos(query: str) -> str:
            """
            Use esta ferramenta OBRIGATORIAMENTE para buscar informações sobre Pablo Ortiz,
            seu currículo, habilidades (FastAPI, React, Docker, etc), portfólio de projetos,
            e tutoriais de tecnologia salvos no banco de dados privado.
            """
            print(
                f"🧠 [AGENTE] Usando a ferramenta de RAG Interno para: {query}")

            contextos = await self.buscar_contexto(query)

            if not contextos:
                return "Não encontrei informações nos documentos internos."

            return "\n\n---\n\n".join(contextos)

        return [pesquisar_documentos_internos, pesquisar_internet]
