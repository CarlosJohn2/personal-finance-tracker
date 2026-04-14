"""Modelo de Meta financeira."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import ModeloBase

if TYPE_CHECKING:
    from src.models.categoria import Categoria


class Meta(ModeloBase):
    """Meta financeira com acompanhamento de progresso.

    Attributes:
        nome: Nome descritivo da meta.
        valor_alvo: Valor total a ser atingido.
        valor_atual: Valor já acumulado.
        data_limite: Data limite para conclusão (opcional).
        ativa: Se a meta está ativa.
        categoria_id: Categoria associada (opcional).
    """

    __tablename__ = "metas"

    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    valor_alvo: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    valor_atual: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), nullable=False, default=Decimal("0.00")
    )
    data_limite: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    categoria_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categorias.id"), nullable=True
    )

    categoria: Mapped[Optional["Categoria"]] = relationship(
        "Categoria", back_populates="metas"
    )

    @property
    def percentual(self) -> float:
        """Percentual de progresso da meta (0 a 100).

        Returns:
            float: Percentual concluído.
        """
        if not self.valor_alvo or self.valor_alvo == 0:
            return 0.0
        return min(float(self.valor_atual / self.valor_alvo * 100), 100.0)

    @property
    def concluida(self) -> bool:
        """Verifica se a meta foi atingida.

        Returns:
            bool: True se valor_atual >= valor_alvo.
        """
        return self.valor_atual >= self.valor_alvo

    @property
    def restante(self) -> Decimal:
        """Valor ainda necessário para atingir a meta.

        Returns:
            Decimal: Valor restante (0 se já concluída).
        """
        diferenca = self.valor_alvo - self.valor_atual
        return max(diferenca, Decimal("0"))

    def __repr__(self) -> str:
        return (
            f"<Meta(id={self.id}, nome='{self.nome}', "
            f"progresso={self.percentual:.1f}%)>"
        )
