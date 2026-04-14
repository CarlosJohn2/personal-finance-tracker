"""Modelo de Categoria de transações financeiras."""
from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import ModeloBase

if TYPE_CHECKING:
    from src.models.meta import Meta
    from src.models.transacao import Transacao


class TipoCategoria(str, Enum):
    """Tipos possíveis de categoria."""

    RECEITA = "receita"
    DESPESA = "despesa"


class Categoria(ModeloBase):
    """Categoria de transação financeira.

    Attributes:
        nome: Nome único da categoria.
        icone: Emoji representando a categoria.
        tipo: Tipo da categoria (receita ou despesa).
        cor: Cor hexadecimal para exibição visual.
    """

    __tablename__ = "categorias"

    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    icone: Mapped[str] = mapped_column(String(10), nullable=False, default="💰")
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    cor: Mapped[str] = mapped_column(String(7), nullable=False, default="#00ff88")

    transacoes: Mapped[List["Transacao"]] = relationship(
        "Transacao", back_populates="categoria", lazy="select"
    )
    metas: Mapped[List["Meta"]] = relationship(
        "Meta", back_populates="categoria", lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Categoria(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
