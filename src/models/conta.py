"""Modelo de Conta financeira."""
from __future__ import annotations

from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import ModeloBase

if TYPE_CHECKING:
    from src.models.transacao import Transacao


class TipoConta(str, Enum):
    """Tipos de conta suportados."""

    CORRENTE = "corrente"
    POUPANCA = "poupanca"
    INVESTIMENTO = "investimento"
    CARTEIRA = "carteira"


ICONES_CONTA = {
    "corrente": "🏦",
    "poupanca": "🐷",
    "investimento": "📈",
    "carteira": "👛",
}


class Conta(ModeloBase):
    """Conta financeira do usuário.

    Attributes:
        nome: Nome identificador da conta.
        tipo: Tipo da conta (corrente, poupança, etc.).
        saldo_inicial: Saldo inicial da conta em reais.
    """

    __tablename__ = "contas"

    nome: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="corrente")
    saldo_inicial: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=Decimal("0.00")
    )

    transacoes: Mapped[List["Transacao"]] = relationship(
        "Transacao", back_populates="conta", lazy="select"
    )

    @property
    def icone(self) -> str:
        """Retorna o ícone correspondente ao tipo de conta."""
        return ICONES_CONTA.get(self.tipo, "💳")

    def __repr__(self) -> str:
        return f"<Conta(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"
