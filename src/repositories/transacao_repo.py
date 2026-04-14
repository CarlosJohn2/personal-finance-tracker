"""Repositório de Transações com consultas especializadas."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy import case, extract, func
from sqlalchemy.orm import Session, joinedload

from src.models.categoria import Categoria
from src.models.conta import Conta
from src.models.transacao import Transacao, TipoTransacao
from src.repositories.base import BaseRepository


class TransacaoRepository(BaseRepository[Transacao]):
    """Repositório especializado para operações com Transacao.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        super().__init__(Transacao, sessao)

    def listar_com_joins(self, limite: int = 100) -> List[Transacao]:
        """Lista transações com conta e categoria pré-carregadas.

        Args:
            limite: Número máximo de registros retornados.

        Returns:
            List[Transacao]: Transações com dados relacionados, ordenadas por data desc.
        """
        return (
            self.sessao.query(Transacao)
            .options(joinedload(Transacao.conta), joinedload(Transacao.categoria))
            .order_by(Transacao.data.desc(), Transacao.id.desc())
            .limit(limite)
            .all()
        )

    def listar_por_periodo(self, data_inicio: date, data_fim: date) -> List[Transacao]:
        """Lista transações dentro de um intervalo de datas.

        Args:
            data_inicio: Data de início (inclusive).
            data_fim: Data de fim (inclusive).

        Returns:
            List[Transacao]: Transações no período.
        """
        return (
            self.sessao.query(Transacao)
            .options(joinedload(Transacao.conta), joinedload(Transacao.categoria))
            .filter(Transacao.data >= data_inicio, Transacao.data <= data_fim)
            .order_by(Transacao.data.desc())
            .all()
        )

    def listar_por_mes_ano(self, mes: int, ano: int) -> List[Transacao]:
        """Lista transações de um mês e ano específicos.

        Args:
            mes: Mês (1–12).
            ano: Ano (ex.: 2025).

        Returns:
            List[Transacao]: Transações do mês ordenadas por data.
        """
        return (
            self.sessao.query(Transacao)
            .options(joinedload(Transacao.conta), joinedload(Transacao.categoria))
            .filter(
                extract("month", Transacao.data) == mes,
                extract("year", Transacao.data) == ano,
            )
            .order_by(Transacao.data.desc())
            .all()
        )

    def calcular_saldo_conta(self, conta_id: int) -> Decimal:
        """Calcula o saldo atual de uma conta (saldo_inicial + receitas - despesas).

        Args:
            conta_id: ID da conta.

        Returns:
            Decimal: Saldo atual.
        """
        conta = self.sessao.get(Conta, conta_id)
        saldo_inicial = Decimal(str(conta.saldo_inicial)) if conta else Decimal("0")

        receitas = Decimal(
            str(
                self.sessao.query(func.coalesce(func.sum(Transacao.valor), 0))
                .filter(
                    Transacao.conta_id == conta_id,
                    Transacao.tipo == TipoTransacao.RECEITA,
                )
                .scalar()
            )
        )

        despesas = Decimal(
            str(
                self.sessao.query(func.coalesce(func.sum(Transacao.valor), 0))
                .filter(
                    Transacao.conta_id == conta_id,
                    Transacao.tipo == TipoTransacao.DESPESA,
                )
                .scalar()
            )
        )

        return saldo_inicial + receitas - despesas

    def totais_por_tipo_mes(self, mes: int, ano: int) -> dict:
        """Calcula totais de receita e despesa de um mês.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            dict: {'receita': Decimal, 'despesa': Decimal}.
        """
        resultado = (
            self.sessao.query(
                Transacao.tipo,
                func.coalesce(func.sum(Transacao.valor), 0),
            )
            .filter(
                extract("month", Transacao.data) == mes,
                extract("year", Transacao.data) == ano,
            )
            .group_by(Transacao.tipo)
            .all()
        )

        totais: dict = {"receita": Decimal("0"), "despesa": Decimal("0")}
        for tipo, total in resultado:
            totais[tipo] = Decimal(str(total))
        return totais

    def gastos_por_categoria(self, mes: int, ano: int) -> List[Tuple]:
        """Retorna despesas agrupadas por categoria em um mês.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            List[Tuple]: [(nome_categoria, icone, total)] ordenado por total desc.
        """
        return (
            self.sessao.query(
                Categoria.nome,
                Categoria.icone,
                Categoria.cor,
                func.coalesce(func.sum(Transacao.valor), 0).label("total"),
            )
            .join(Categoria, Transacao.categoria_id == Categoria.id)
            .filter(
                extract("month", Transacao.data) == mes,
                extract("year", Transacao.data) == ano,
                Transacao.tipo == TipoTransacao.DESPESA,
            )
            .group_by(Categoria.nome, Categoria.icone, Categoria.cor)
            .order_by(func.sum(Transacao.valor).desc())
            .all()
        )

    def historico_mensal_ano(self, ano: int) -> List[Tuple]:
        """Histórico mensal de receitas e despesas de um ano.

        Args:
            ano: Ano.

        Returns:
            List[Tuple]: [(mes, tipo, total)].
        """
        return (
            self.sessao.query(
                extract("month", Transacao.data).label("mes"),
                Transacao.tipo,
                func.coalesce(func.sum(Transacao.valor), 0).label("total"),
            )
            .filter(extract("year", Transacao.data) == ano)
            .group_by(
                extract("month", Transacao.data),
                Transacao.tipo,
            )
            .order_by("mes")
            .all()
        )

    def saldo_diario(self, mes: int, ano: int, conta_id: int) -> List[Tuple]:
        """Retorna o saldo acumulado dia a dia de um mês.

        Args:
            mes: Mês (1–12).
            ano: Ano.
            conta_id: ID da conta.

        Returns:
            List[Tuple]: [(data, saldo_diario_liquido)].
        """
        return (
            self.sessao.query(
                Transacao.data,
                func.sum(
                    case(
                        (Transacao.tipo == TipoTransacao.RECEITA, Transacao.valor),
                        else_=-Transacao.valor,
                    )
                ).label("liquido"),
            )
            .filter(
                Transacao.conta_id == conta_id,
                extract("month", Transacao.data) == mes,
                extract("year", Transacao.data) == ano,
            )
            .group_by(Transacao.data)
            .order_by(Transacao.data)
            .all()
        )
