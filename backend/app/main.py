from fastapi import FastAPI, Depends
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.api.deps import get_db
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import documents, chat

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="API do Agente Inteligente Synca (RAG Local)",
    version="1.0.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    documents.router, prefix=f"{settings.API_V1_STR}/docs", tags=["Documentos"])
app.include_router(
    chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["Inteligência Artificial"])


@app.get("/health", tags=["Status"])
async def health_check(db: AsyncSession = Depends(get_db)):

    try:
        await db.execute(text('SELECT 1'))
        db_status = "Conectado"
        db_msg = "Banco de dados conectado PORT:5444"
    except Exception as e:
        db_status = "erro"
        db_msg = f"Falha na conexão: {str(e)}"

    return {
        "status": "operacional",
        "banco_dados": {
            "status": db_status,
            "mensagem": db_msg
        },
        "sistema": "Synca",
        "versao": "1.0.0",
        "mensagem": "Tudo pronto"
    }


@app.get("/")
async def root():
    return {"mensagem": "Synca API."}
