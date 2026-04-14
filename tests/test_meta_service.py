"""Testes unitários do MetaService."""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.services.meta_service import MetaService


class TestCriarMeta:
    """Testes para criação de metas."""

    def test_criar_meta_simples(self, sessao):
        svc = MetaService(sessao)
        meta = svc.criar(nome="Reserva de emergência", valor_alvo=Decimal("10000.00"))
        assert meta.id is not None
        assert meta.nome == "Reserva de emergência"
        assert meta.valor_atual == Decimal("0.00")
        assert meta.ativa is True

    def test_criar_meta_com_prazo(self, sessao):
        svc = MetaService(sessao)
        prazo = date(2026, 12, 31)
        meta = svc.criar(
            nome="Carro novo",
            valor_alvo=Decimal("50000.00"),
            data_limite=prazo,
        )
        assert meta.data_limite == prazo

    def test_valor_alvo_zero_levanta_erro(self, sessao):
        svc = MetaService(sessao)
        with pytest.raises(ValueError, match="maior que zero"):
            svc.criar(nome="Inválida", valor_alvo=Decimal("0"))

    def test_valor_alvo_negativo_levanta_erro(self, sessao):
        svc = MetaService(sessao)
        with pytest.raises(ValueError, match="maior que zero"):
            svc.criar(nome="Inválida", valor_alvo=Decimal("-100"))


class TestDepositar:
    """Testes para aporte em metas."""

    def test_depositar_aumenta_valor_atual(self, sessao, meta_viagem):
        svc = MetaService(sessao)
        meta = svc.depositar(meta_viagem.id, Decimal("500.00"))
        assert meta.valor_atual == Decimal("3000.00")

    def test_depositar_zero_levanta_erro(self, sessao, meta_viagem):
        svc = MetaService(sessao)
        with pytest.raises(ValueError, match="maior que zero"):
            svc.depositar(meta_viagem.id, Decimal("0"))

    def test_depositar_meta_inexistente(self, sessao):
        svc = MetaService(sessao)
        with pytest.raises(ValueError, match="não encontrada"):
            svc.depositar(9999, Decimal("100.00"))

    def test_depositar_meta_inativa_levanta_erro(self, sessao):
        svc = MetaService(sessao)
        meta = svc.criar(nome="Inativa", valor_alvo=Decimal("1000.00"))
        svc.encerrar(meta.id)
        with pytest.raises(ValueError, match="inativa"):
            svc.depositar(meta.id, Decimal("100.00"))


class TestPercentual:
    """Testes da propriedade percentual."""

    def test_percentual_zero(self, sessao):
        svc = MetaService(sessao)
        meta = svc.criar(nome="Nova", valor_alvo=Decimal("1000.00"))
        assert meta.percentual == 0.0

    def test_percentual_cinquenta_porcento(self, sessao, meta_viagem):
        # meta_viagem: atual=2500, alvo=10000 → 25%
        assert meta_viagem.percentual == 25.0

    def test_percentual_concluida(self, sessao):
        svc = MetaService(sessao)
        meta = svc.criar(nome="Concluída", valor_alvo=Decimal("1000.00"))
        svc.depositar(meta.id, Decimal("1000.00"))
        meta_atualizada = svc.obter(meta.id)
        assert meta_atualizada.percentual == 100.0
        assert meta_atualizada.concluida is True


class TestAlertas:
    """Testes de verificação de alertas."""

    def test_alerta_meta_concluida(self, sessao):
        svc = MetaService(sessao)
        meta = svc.criar(nome="Atingida", valor_alvo=Decimal("500.00"))
        svc.depositar(meta.id, Decimal("500.00"))
        alertas = svc.verificar_alertas()
        assert any("atingida" in a.lower() or "✅" in a for a in alertas)

    def test_alerta_meta_vencida(self, sessao):
        svc = MetaService(sessao)
        ontem = date.today() - timedelta(days=1)
        svc.criar(
            nome="Vencida",
            valor_alvo=Decimal("1000.00"),
            data_limite=ontem,
        )
        alertas = svc.verificar_alertas()
        assert any("VENCIDA" in a or "vencida" in a.lower() for a in alertas)

    def test_sem_alertas_quando_nenhuma_meta(self, sessao):
        svc = MetaService(sessao)
        alertas = svc.verificar_alertas()
        assert alertas == []


class TestEncerrar:
    """Testes para encerramento de metas."""

    def test_encerrar_desativa_meta(self, sessao, meta_viagem):
        svc = MetaService(sessao)
        meta = svc.encerrar(meta_viagem.id)
        assert meta.ativa is False

    def test_encerrar_inexistente_levanta_erro(self, sessao):
        svc = MetaService(sessao)
        with pytest.raises(ValueError, match="não encontrada"):
            svc.encerrar(9999)
