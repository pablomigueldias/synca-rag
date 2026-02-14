from typing import Any
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

class Base(DeclarativeBase):
    id: Any
    __name__: str

    @declared_attr #type: ignore
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"