"""Testes unitários do TransacaoService."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.models.conta import Conta
from src.models.categoria import Categoria
from src.models.transacao import Transacao
from src.services.transacao_service import TransacaoService


class TestAdicionarTransacao:
    """Testes para o método TransacaoService.adicionar."""

    def test_adicionar_receita_com_sucesso(self, sessao, conta_corrente, categoria_salario):
        svc = TransacaoService(sessao)
        t = svc.adicionar(
            descricao="Salário",
            valor=Decimal("5000.00"),
            tipo="receita",
            data=date(2025, 4, 1),
            conta_id=conta_corrente.id,
            categoria_id=categoria_salario.id,
        )
        assert t.id is not None
        assert t.tipo == "receita"
        assert t.valor == Decimal("5000.00")

    def test_adicionar_despesa_com_sucesso(self, sessao, conta_corrente, categoria_alimentacao):
        svc = TransacaoService(sessao)
        t = svc.adicionar(
            descricao="Aluguel",
            valor=Decimal("1500.00"),
            tipo="despesa",
            data=date(2025, 4, 10),
            conta_id=conta_corrente.id,
            categoria_id=categoria_alimentacao.id,
        )
        assert t.tipo == "despesa"
        assert t.valor == Decimal("1500.00")

    def test_adicionar_sem_categoria(self, sessao, conta_corrente):
        svc = TransacaoService(sessao)
        t = svc.adicionar(
            descricao="Pix diverso",
            valor=Decimal("100.00"),
            tipo="despesa",
            data=date(2025, 4, 15),
            conta_id=conta_corrente.id,
        )
        assert t.categoria_id is None

    def test_valor_zero_levanta_erro(self, sessao, conta_corrente):
        svc = TransacaoService(sessao)
        with pytest.raises(ValueError, match="maior que zero"):
            svc.adicionar(
                descricao="Inválida",
                valor=Decimal("0"),
                tipo="despesa",
                data=date(2025, 4, 1),
                conta_id=conta_corrente.id,
            )

    def test_valor_negativo_levanta_erro(self, sessao, conta_corrente):
        svc = TransacaoService(sessao)
        with pytest.raises(ValueError, match="maior que zero"):
            svc.adicionar(
                descricao="Inválida",
                valor=Decimal("-50.00"),
                tipo="despesa",
                data=date(2025, 4, 1),
                conta_id=conta_corrente.id,
            )

    def test_conta_inexistente_levanta_erro(self, sessao):
        svc = TransacaoService(sessao)
        with pytest.raises(ValueError, match="não encontrada"):
            svc.adicionar(
                descricao="Teste",
                valor=Decimal("100.00"),
                tipo="despesa",
                data=date(2025, 4, 1),
                conta_id=9999,
            )

    def test_tipo_invalido_levanta_erro(self, sessao, conta_corrente):
        svc = TransacaoService(sessao)
        with pytest.raises(ValueError, match="Tipo deve ser"):
            svc.adicionar(
                descricao="Teste",
                valor=Decimal("100.00"),
                tipo="outro",
                data=date(2025, 4, 1),
                conta_id=conta_corrente.id,
            )

    def test_categoria_tipo_errado_levanta_erro(
        self, sessao, conta_corrente, categoria_alimentacao
    ):
        """Categoria de despesa não pode ser usada em receita."""
        svc = TransacaoService(sessao)
        with pytest.raises(ValueError, match="tipo"):
            svc.adicionar(
                descricao="Receita",
                valor=Decimal("100.00"),
                tipo="receita",
                data=date(2025, 4, 1),
                conta_id=conta_corrente.id,
                categoria_id=categoria_alimentacao.id,
            )


class TestSaldo:
    """Testes de cálculo de saldo."""

    def test_saldo_inicial_sem_transacoes(self, sessao, conta_corrente):
        svc = TransacaoService(sessao)
        saldo = svc.saldo_conta(conta_corrente.id)
        assert saldo == Decimal("2000.00")

    def test_saldo_apos_receita(self, sessao, conta_corrente, categoria_salario):
        svc = TransacaoService(sessao)
        svc.adicionar(
            descricao="Salário",
            valor=Decimal("3000.00"),
            tipo="receita",
            data=date(2025, 4, 1),
            conta_id=conta_corrente.id,
            categoria_id=categoria_salario.id,
        )
        saldo = svc.saldo_conta(conta_corrente.id)
        assert saldo == Decimal("5000.00")

    def test_saldo_apos_despesa(self, sessao, conta_corrente, categoria_alimentacao):
        svc = TransacaoService(sessao)
        svc.adicionar(
            descricao="Conta de luz",
            valor=Decimal("200.00"),
            tipo="despesa",
            data=date(2025, 4, 5),
            conta_id=conta_corrente.id,
            categoria_id=categoria_alimentacao.id,
        )
        saldo = svc.saldo_conta(conta_corrente.id)
        assert saldo == Decimal("1800.00")

    def test_saldo_total_multiplas_contas(self, sessao, conta_corrente, conta_poupanca):
        svc = TransacaoService(sessao)
        saldo = svc.saldo_total()
        assert saldo == Decimal("7000.00")  # 2000 + 5000


class TestRemoverTransacao:
    """Testes de remoção de transações."""

    def test_remover_existente(self, sessao, conta_corrente, transacao_despesa):
        svc = TransacaoService(sessao)
        svc.remover(transacao_despesa.id)
        assert svc.obter(transacao_despesa.id) is None

    def test_remover_inexistente_levanta_erro(self, sessao):
        svc = TransacaoService(sessao)
        with pytest.raises(ValueError, match="não encontrada"):
            svc.remover(9999)


class TestListar:
    """Testes de listagem de transações."""

    def test_listar_por_mes(
        self, sessao, conta_corrente, transacao_receita, transacao_despesa
    ):
        svc = TransacaoService(sessao)
        transacoes = svc.listar_por_mes(4, 2025)
        assert len(transacoes) == 2

    def test_listar_mes_sem_transacoes(self, sessao):
        svc = TransacaoService(sessao)
        transacoes = svc.listar_por_mes(1, 2020)
        assert transacoes == []
