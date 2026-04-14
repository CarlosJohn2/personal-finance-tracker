"""Repositório de Contas financeiras."""
from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from src.models.conta import Conta
from src.repositories.base import BaseRepository


class ContaRepository(BaseRepository[Conta]):
    """Repositório especializado para operações com Conta.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        super().__init__(Conta, sessao)

    def buscar_por_nome(self, nome: str) -> Optional[Conta]:
        """Busca conta pelo nome exato.

        Args:
            nome: Nome da conta.

        Returns:
            Optional[Conta]: Conta encontrada ou None.
        """
        return self.sessao.query(Conta).filter(Conta.nome == nome).first()

    def listar_ordenado(self):
        """Lista contas ordenadas por nome.

        Returns:
            List[Conta]: Contas ordenadas.
        """
        return self.sessao.query(Conta).order_by(Conta.nome).all()
