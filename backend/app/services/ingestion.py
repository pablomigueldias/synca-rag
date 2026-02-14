import shutil
import os
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

from app.core.config import settings
from app.models.rag_models import Document, DocumentChunk


class IngestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embeddings_model = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url=settings.OLLAMA_BASE_URL
        )

    async def process_pdf(self, file: UploadFile):

        temp_filename = f"temp_{file.filename}"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        try:
            ext = os.path.splitext(file.filename)[1].lower() #type:ignore
            file_type = "md" if ext == ".md" else "pdf"

            db_doc = Document(
                filename=file.filename,
                file_type=file_type,
                created_at=datetime.now()
            )
            self.db.add(db_doc)
            await self.db.flush()

            if ext == ".pdf":
                loader = PyPDFLoader(temp_filename)
            elif ext == ".md":
                loader = TextLoader(temp_filename, encoding="utf-8")
            else:
                raise ValueError("Formato não suportado")

            pages = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(pages)

            print(
                f" Processando {len(chunks)} chunks para '{file.filename}'...")

            for i, chunk in enumerate(chunks):

                vector = self.embeddings_model.embed_query(chunk.page_content)

                db_chunk = DocumentChunk(
                    document_id=db_doc.id,
                    content=chunk.page_content,
                    chunk_index=i,
                    embedding=vector
                )
                self.db.add(db_chunk)

            await self.db.commit()
            return {"mensagem": "Processamento concluído", "chunks_criados": len(chunks), "doc_id": db_doc.id}

        except Exception as e:
            await self.db.rollback()
            raise e
        finally:

            if os.path.exists(temp_filename):
                os.remove(temp_filename)
