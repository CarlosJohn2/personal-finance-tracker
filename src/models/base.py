"""Modelo base abstrato com campos de auditoria."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarativa do SQLAlchemy 2.0."""

    def to_dict(self) -> dict[str, Any]:
        """Converte o modelo para dicionário.

        Returns:
            dict: Representação do modelo em dicionário.
        """
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class ModeloBase(Base):
    """Modelo base com campos de auditoria comuns.

    Attributes:
        id: Chave primária auto-incrementada.
        criado_em: Timestamp de criação (preenchido automaticamente).
        atualizado_em: Timestamp da última atualização.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
