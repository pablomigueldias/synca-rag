from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.services.rag_service import RAGService

router = APIRouter()


class ChatRequest(BaseModel):
    pergunta: str
    session_id: str


@router.post("/", status_code=200)
async def chat_com_documentos(
    dados: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = RAGService(db)
        # type: ignore
        resultado = await service.responder(dados.pergunta, dados.session_id)
        return resultado
    except Exception as e:
        print(f"Erro no RAG: {e}")
        raise HTTPException(
            status_code=500, detail="Ocorreu um erro ao processar sua pergunta.")
