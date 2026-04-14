"""Repositório de Metas financeiras."""
from __future__ import annotations

from typing import List

from sqlalchemy import asc, case
from sqlalchemy.orm import Session, joinedload

from src.models.meta import Meta
from src.repositories.base import BaseRepository


class MetaRepository(BaseRepository[Meta]):
    """Repositório especializado para operações com Meta.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        super().__init__(Meta, sessao)

    def listar_ativas(self) -> List[Meta]:
        """Lista metas ativas com categoria pré-carregada.

        Returns:
            List[Meta]: Metas ativas ordenadas por data_limite (nulos por último).
        """
        return (
            self.sessao.query(Meta)
            .options(joinedload(Meta.categoria))
            .filter(Meta.ativa == True)  # noqa: E712
            .order_by(case((Meta.data_limite == None, 1), else_=0), Meta.data_limite.asc())
            .all()
        )

    def listar_todas(self) -> List[Meta]:
        """Lista todas as metas (ativas e inativas).

        Returns:
            List[Meta]: Todas as metas ordenadas por status e data.
        """
        return (
            self.sessao.query(Meta)
            .options(joinedload(Meta.categoria))
            .order_by(Meta.ativa.desc(), case((Meta.data_limite == None, 1), else_=0), Meta.data_limite.asc())
            .all()
        )
