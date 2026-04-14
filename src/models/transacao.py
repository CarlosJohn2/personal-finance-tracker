"""Modelo de Transação financeira."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import ModeloBase

if TYPE_CHECKING:
    from src.models.categoria import Categoria
    from src.models.conta import Conta


class TipoTransacao(str, Enum):
    """Tipos de transação possíveis."""

    RECEITA = "receita"
    DESPESA = "despesa"


class Transacao(ModeloBase):
    """Transação financeira (receita ou despesa).

    Attributes:
        descricao: Descrição da transação.
        valor: Valor em reais (sempre positivo).
        tipo: Tipo da transação (receita ou despesa).
        data: Data de competência.
        conta_id: Referência à conta associada.
        categoria_id: Referência à categoria (opcional).
        observacao: Observação adicional (opcional).
    """

    __tablename__ = "transacoes"
    __table_args__ = (
        Index("ix_transacoes_data", "data"),
        Index("ix_transacoes_conta_data", "conta_id", "data"),
        Index("ix_transacoes_categoria", "categoria_id"),
        Index("ix_transacoes_tipo_data", "tipo", "data"),
    )

    descricao: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False)
    data: Mapped[date] = mapped_column(Date, nullable=False)
    conta_id: Mapped[int] = mapped_column(ForeignKey("contas.id"), nullable=False)
    categoria_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categorias.id"), nullable=True
    )
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    conta: Mapped["Conta"] = relationship("Conta", back_populates="transacoes")
    categoria: Mapped[Optional["Categoria"]] = relationship(
        "Categoria", back_populates="transacoes"
    )

    def __repr__(self) -> str:
        return (
            f"<Transacao(id={self.id}, descricao='{self.descricao}', "
            f"valor={self.valor}, tipo='{self.tipo}', data={self.data})>"
        )
