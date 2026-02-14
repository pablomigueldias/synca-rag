from sqlalchemy import text
from app.db.session import engine
from app.db.base_class import Base
from app.models.rag_models import Document, DocumentChunk, ChatMessage


async def init_models():
    async with engine.begin() as conn:

        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        
      
        await conn.run_sync(Base.metadata.create_all)
        
        print("Tabelas e Extensão Vector criadas com sucesso!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_models())