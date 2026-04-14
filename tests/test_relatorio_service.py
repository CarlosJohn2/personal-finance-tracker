"""Testes unitários do RelatorioService."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.services.relatorio_service import RelatorioService
from src.services.transacao_service import TransacaoService


@pytest.fixture
def dados_abril(sessao, conta_corrente, categoria_salario, categoria_alimentacao):
    """Cria transações de abril/2025 para testes."""
    svc = TransacaoService(sessao)
    svc.adicionar(
        descricao="Salário",
        valor=Decimal("6000.00"),
        tipo="receita",
        data=date(2025, 4, 1),
        conta_id=conta_corrente.id,
        categoria_id=categoria_salario.id,
    )
    svc.adicionar(
        descricao="Supermercado",
        valor=Decimal("800.00"),
        tipo="despesa",
        data=date(2025, 4, 10),
        conta_id=conta_corrente.id,
        categoria_id=categoria_alimentacao.id,
    )
    svc.adicionar(
        descricao="Restaurante",
        valor=Decimal("200.00"),
        tipo="despesa",
        data=date(2025, 4, 15),
        conta_id=conta_corrente.id,
        categoria_id=categoria_alimentacao.id,
    )
    return True


class TestResumoMensal:
    """Testes para resumo mensal."""

    def test_resumo_com_dados(self, sessao, dados_abril):
        svc = RelatorioService(sessao)
        resumo = svc.resumo_mensal(4, 2025)

        assert resumo["receita"] == Decimal("6000.00")
        assert resumo["despesa"] == Decimal("1000.00")
        assert resumo["saldo"] == Decimal("5000.00")
        assert resumo["total_transacoes"] == 3
        assert resumo["nome_mes"] == "Abril"

    def test_resumo_mes_vazio(self, sessao):
        svc = RelatorioService(sessao)
        resumo = svc.resumo_mensal(1, 2000)

        assert resumo["receita"] == Decimal("0")
        assert resumo["despesa"] == Decimal("0")
        assert resumo["saldo"] == Decimal("0")
        assert resumo["total_transacoes"] == 0

    def test_resumo_categorias(self, sessao, dados_abril):
        svc = RelatorioService(sessao)
        resumo = svc.resumo_mensal(4, 2025)

        assert len(resumo["categorias"]) == 1
        nome, _, _, total = resumo["categorias"][0]
        assert nome == "Alimentação"
        assert total == Decimal("1000.00")


class TestHistoricoAnual:
    """Testes para histórico anual."""

    def test_historico_estrutura(self, sessao):
        svc = RelatorioService(sessao)
        historico = svc.historico_anual(2025)

        assert "meses" in historico
        assert len(historico["meses"]) == 12
        for m in range(1, 13):
            assert m in historico["meses"]
            assert "receita" in historico["meses"][m]
            assert "despesa" in historico["meses"][m]

    def test_historico_com_dados(self, sessao, dados_abril):
        svc = RelatorioService(sessao)
        historico = svc.historico_anual(2025)

        assert historico["meses"][4]["receita"] == Decimal("6000.00")
        assert historico["meses"][4]["despesa"] == Decimal("1000.00")
        assert historico["total_receita"] == Decimal("6000.00")
        assert historico["total_despesa"] == Decimal("1000.00")
        assert historico["saldo_anual"] == Decimal("5000.00")

    def test_meses_sem_dados_sao_zero(self, sessao, dados_abril):
        svc = RelatorioService(sessao)
        historico = svc.historico_anual(2025)

        assert historico["meses"][1]["receita"] == Decimal("0")
        assert historico["meses"][3]["despesa"] == Decimal("0")
