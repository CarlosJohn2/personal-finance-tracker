"""Repositório base genérico com operações CRUD."""
from __future__ import annotations

from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy.orm import Session

from src.models.base import ModeloBase

T = TypeVar("T", bound=ModeloBase)


class BaseRepository(Generic[T]):
    """Repositório base com operações CRUD genéricas.

    Args:
        modelo: Classe do modelo SQLAlchemy.
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, modelo: Type[T], sessao: Session) -> None:
        self.modelo = modelo
        self.sessao = sessao

    def criar(self, **dados) -> T:
        """Cria e persiste um novo registro.

        Args:
            **dados: Campos do modelo.

        Returns:
            T: Instância criada e vinculada à sessão.
        """
        instancia = self.modelo(**dados)
        self.sessao.add(instancia)
        self.sessao.flush()
        self.sessao.refresh(instancia)
        return instancia

    def obter(self, id: int) -> Optional[T]:
        """Busca um registro pelo ID.

        Args:
            id: Chave primária do registro.

        Returns:
            Optional[T]: Registro encontrado ou None.
        """
        return self.sessao.get(self.modelo, id)

    def listar(self) -> List[T]:
        """Retorna todos os registros da tabela.

        Returns:
            List[T]: Lista completa de registros.
        """
        return self.sessao.query(self.modelo).all()

    def atualizar(self, id: int, **dados) -> Optional[T]:
        """Atualiza campos de um registro existente.

        Args:
            id: Chave primária do registro.
            **dados: Campos a serem atualizados.

        Returns:
            Optional[T]: Registro atualizado ou None se não encontrado.
        """
        instancia = self.obter(id)
        if instancia:
            for chave, valor in dados.items():
                setattr(instancia, chave, valor)
            self.sessao.flush()
        return instancia

    def deletar(self, id: int) -> bool:
        """Remove um registro pelo ID.

        Args:
            id: Chave primária do registro.

        Returns:
            bool: True se removido com sucesso, False se não encontrado.
        """
        instancia = self.obter(id)
        if instancia:
            self.sessao.delete(instancia)
            self.sessao.flush()
            return True
        return False

    def contar(self) -> int:
        """Retorna o total de registros na tabela.

        Returns:
            int: Contagem de registros.
        """
        return self.sessao.query(self.modelo).count()
