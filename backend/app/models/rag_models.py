from datetime import datetime
from typing import List, Optional, Literal
from sqlalchemy import String, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.db.base_class import Base


class Document(Base):
    __tablename__ = "documents"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, index=True)
    file_type: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    chunks: Mapped[List["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"  # type: ignore

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))

    content: Mapped[str] = mapped_column(Text)

    chunk_index: Mapped[int] = mapped_column()

    embedding: Mapped[List[float]] = mapped_column(Vector(768))

    document: Mapped["Document"] = relationship(back_populates="chunks")


class ChatMessage(Base):
    __tablename__ = "chat_messages" #type:ignore

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[str] = mapped_column(
        String, index=True)
    role: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
