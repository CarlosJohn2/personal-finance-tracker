"""Repositório de Categorias."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.categoria import Categoria
from src.repositories.base import BaseRepository


class CategoriaRepository(BaseRepository[Categoria]):
    """Repositório especializado para operações com Categoria.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        super().__init__(Categoria, sessao)

    def listar_por_tipo(self, tipo: str) -> List[Categoria]:
        """Lista categorias filtradas por tipo.

        Args:
            tipo: 'receita' ou 'despesa'.

        Returns:
            List[Categoria]: Categorias do tipo especificado, ordenadas por nome.
        """
        return (
            self.sessao.query(Categoria)
            .filter(Categoria.tipo == tipo)
            .order_by(Categoria.nome)
            .all()
        )

    def buscar_por_nome(self, nome: str) -> Optional[Categoria]:
        """Busca categoria pelo nome exato.

        Args:
            nome: Nome da categoria.

        Returns:
            Optional[Categoria]: Categoria encontrada ou None.
        """
        return (
            self.sessao.query(Categoria).filter(Categoria.nome == nome).first()
        )

    def listar_ordenado(self) -> List[Categoria]:
        """Lista todas as categorias ordenadas por tipo e nome.

        Returns:
            List[Categoria]: Lista ordenada.
        """
        return (
            self.sessao.query(Categoria)
            .order_by(Categoria.tipo, Categoria.nome)
            .all()
        )
