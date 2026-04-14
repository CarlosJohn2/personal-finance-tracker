"""Fixtures compartilhadas entre todos os testes."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.models.base import Base
from src.models.categoria import Categoria, TipoCategoria
from src.models.conta import Conta
from src.models.meta import Meta
from src.models.transacao import Transacao, TipoTransacao


@pytest.fixture(scope="function")
def engine():
    """Cria um banco SQLite em memória para cada teste.

    Yields:
        Engine: Engine SQLAlchemy com schema completo.
    """
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)
    eng.dispose()


@pytest.fixture(scope="function")
def sessao(engine) -> Session:
    """Fornece uma sessão de banco de dados para o teste.

    Yields:
        Session: Sessão SQLAlchemy ativa.
    """
    SessionTest = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    s = SessionTest()
    yield s
    s.rollback()
    s.close()


@pytest.fixture
def conta_corrente(sessao: Session) -> Conta:
    """Conta corrente com saldo inicial de R$ 2.000,00."""
    conta = Conta(
        nome="Conta Corrente",
        tipo="corrente",
        saldo_inicial=Decimal("2000.00"),
    )
    sessao.add(conta)
    sessao.commit()
    sessao.refresh(conta)
    return conta


@pytest.fixture
def conta_poupanca(sessao: Session) -> Conta:
    """Conta poupança com saldo inicial de R$ 5.000,00."""
    conta = Conta(
        nome="Poupança",
        tipo="poupanca",
        saldo_inicial=Decimal("5000.00"),
    )
    sessao.add(conta)
    sessao.commit()
    sessao.refresh(conta)
    return conta


@pytest.fixture
def categoria_alimentacao(sessao: Session) -> Categoria:
    """Categoria de despesa: Alimentação."""
    cat = Categoria(
        nome="Alimentação",
        icone="🍔",
        tipo=TipoCategoria.DESPESA,
        cor="#ff5555",
    )
    sessao.add(cat)
    sessao.commit()
    sessao.refresh(cat)
    return cat


@pytest.fixture
def categoria_salario(sessao: Session) -> Categoria:
    """Categoria de receita: Salário."""
    cat = Categoria(
        nome="Salário",
        icone="💼",
        tipo=TipoCategoria.RECEITA,
        cor="#00ff88",
    )
    sessao.add(cat)
    sessao.commit()
    sessao.refresh(cat)
    return cat


@pytest.fixture
def transacao_receita(sessao: Session, conta_corrente: Conta, categoria_salario: Categoria) -> Transacao:
    """Transação de receita padrão para testes."""
    t = Transacao(
        descricao="Salário de Abril",
        valor=Decimal("5000.00"),
        tipo=TipoTransacao.RECEITA,
        data=date(2025, 4, 1),
        conta_id=conta_corrente.id,
        categoria_id=categoria_salario.id,
    )
    sessao.add(t)
    sessao.commit()
    sessao.refresh(t)
    return t


@pytest.fixture
def transacao_despesa(sessao: Session, conta_corrente: Conta, categoria_alimentacao: Categoria) -> Transacao:
    """Transação de despesa padrão para testes."""
    t = Transacao(
        descricao="Supermercado",
        valor=Decimal("350.00"),
        tipo=TipoTransacao.DESPESA,
        data=date(2025, 4, 5),
        conta_id=conta_corrente.id,
        categoria_id=categoria_alimentacao.id,
    )
    sessao.add(t)
    sessao.commit()
    sessao.refresh(t)
    return t


@pytest.fixture
def meta_viagem(sessao: Session) -> Meta:
    """Meta de poupança para viagem."""
    meta = Meta(
        nome="Viagem para Europa",
        valor_alvo=Decimal("10000.00"),
        valor_atual=Decimal("2500.00"),
        data_limite=date(2026, 6, 1),
        ativa=True,
    )
    sessao.add(meta)
    sessao.commit()
    sessao.refresh(meta)
    return meta
