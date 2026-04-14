"""Serviço de regras de negócio para Transações."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from src.models.transacao import Transacao
from src.repositories.categoria_repo import CategoriaRepository
from src.repositories.conta_repo import ContaRepository
from src.repositories.transacao_repo import TransacaoRepository


class TransacaoService:
    """Orquestra regras de negócio para transações financeiras.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        self.repo = TransacaoRepository(sessao)
        self.conta_repo = ContaRepository(sessao)
        self.categoria_repo = CategoriaRepository(sessao)

    def adicionar(
        self,
        descricao: str,
        valor: Decimal,
        tipo: str,
        data: date,
        conta_id: int,
        categoria_id: Optional[int] = None,
        observacao: Optional[str] = None,
    ) -> Transacao:
        """Adiciona uma nova transação após validações.

        Args:
            descricao: Descrição da transação.
            valor: Valor positivo em reais.
            tipo: 'receita' ou 'despesa'.
            data: Data de competência.
            conta_id: ID da conta associada.
            categoria_id: ID da categoria (opcional).
            observacao: Observação adicional (opcional).

        Returns:
            Transacao: Transação criada.

        Raises:
            ValueError: Se valor for zero/negativo ou conta não existir.
        """
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        if tipo not in ("receita", "despesa"):
            raise ValueError("Tipo deve ser 'receita' ou 'despesa'.")

        conta = self.conta_repo.obter(conta_id)
        if not conta:
            raise ValueError(f"Conta ID {conta_id} não encontrada.")

        if categoria_id:
            categoria = self.categoria_repo.obter(categoria_id)
            if not categoria:
                raise ValueError(f"Categoria ID {categoria_id} não encontrada.")
            if categoria.tipo != tipo:
                raise ValueError(
                    f"A categoria '{categoria.nome}' é do tipo '{categoria.tipo}', "
                    f"mas a transação é do tipo '{tipo}'."
                )

        return self.repo.criar(
            descricao=descricao.strip(),
            valor=valor,
            tipo=tipo,
            data=data,
            conta_id=conta_id,
            categoria_id=categoria_id,
            observacao=observacao,
        )

    def editar(self, id: int, **dados) -> Transacao:
        """Edita campos de uma transação existente.

        Args:
            id: ID da transação.
            **dados: Campos a atualizar.

        Returns:
            Transacao: Transação atualizada.

        Raises:
            ValueError: Se a transação não for encontrada.
        """
        if "valor" in dados and dados["valor"] <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        transacao = self.repo.atualizar(id, **dados)
        if not transacao:
            raise ValueError(f"Transação ID {id} não encontrada.")
        return transacao

    def remover(self, id: int) -> None:
        """Remove uma transação pelo ID.

        Args:
            id: ID da transação.

        Raises:
            ValueError: Se a transação não for encontrada.
        """
        if not self.repo.deletar(id):
            raise ValueError(f"Transação ID {id} não encontrada.")

    def listar(self, limite: int = 50) -> List[Transacao]:
        """Lista as transações mais recentes.

        Args:
            limite: Máximo de registros retornados.

        Returns:
            List[Transacao]: Transações ordenadas por data desc.
        """
        return self.repo.listar_com_joins(limite=limite)

    def listar_por_mes(self, mes: int, ano: int) -> List[Transacao]:
        """Lista transações de um mês específico.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            List[Transacao]: Transações do mês.
        """
        return self.repo.listar_por_mes_ano(mes, ano)

    def saldo_conta(self, conta_id: int) -> Decimal:
        """Calcula o saldo atual de uma conta.

        Args:
            conta_id: ID da conta.

        Returns:
            Decimal: Saldo atual (pode ser negativo).
        """
        return self.repo.calcular_saldo_conta(conta_id)

    def saldo_total(self) -> Decimal:
        """Calcula o saldo consolidado de todas as contas.

        Returns:
            Decimal: Saldo total.
        """
        contas = self.conta_repo.listar()
        return sum((self.saldo_conta(c.id) for c in contas), Decimal("0"))

    def obter(self, id: int) -> Optional[Transacao]:
        """Obtém uma transação pelo ID.

        Args:
            id: ID da transação.

        Returns:
            Optional[Transacao]: Transação ou None.
        """
        return self.repo.obter(id)
