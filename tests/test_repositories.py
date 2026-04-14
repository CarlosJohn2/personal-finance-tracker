"""Testes da camada de repositórios."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from src.models.categoria import Categoria, TipoCategoria
from src.models.conta import Conta
from src.repositories.base import BaseRepository
from src.repositories.categoria_repo import CategoriaRepository
from src.repositories.conta_repo import ContaRepository
from src.repositories.transacao_repo import TransacaoRepository


class TestBaseRepository:
    """Testes do repositório base genérico."""

    def test_criar_e_obter(self, sessao):
        repo = ContaRepository(sessao)
        conta = repo.criar(nome="Teste", tipo="corrente", saldo_inicial=Decimal("0"))
        assert conta.id is not None
        obtida = repo.obter(conta.id)
        assert obtida.nome == "Teste"

    def test_obter_inexistente_retorna_none(self, sessao):
        repo = ContaRepository(sessao)
        assert repo.obter(9999) is None

    def test_listar_todos(self, sessao, conta_corrente, conta_poupanca):
        repo = ContaRepository(sessao)
        contas = repo.listar()
        assert len(contas) == 2

    def test_atualizar_campo(self, sessao, conta_corrente):
        repo = ContaRepository(sessao)
        repo.atualizar(conta_corrente.id, nome="Conta Principal")
        atualizada = repo.obter(conta_corrente.id)
        assert atualizada.nome == "Conta Principal"

    def test_atualizar_inexistente_retorna_none(self, sessao):
        repo = ContaRepository(sessao)
        resultado = repo.atualizar(9999, nome="Fantasma")
        assert resultado is None

    def test_deletar(self, sessao, conta_corrente):
        repo = ContaRepository(sessao)
        resultado = repo.deletar(conta_corrente.id)
        assert resultado is True
        assert repo.obter(conta_corrente.id) is None

    def test_deletar_inexistente_retorna_false(self, sessao):
        repo = ContaRepository(sessao)
        assert repo.deletar(9999) is False

    def test_contar(self, sessao, conta_corrente, conta_poupanca):
        repo = ContaRepository(sessao)
        assert repo.contar() == 2


class TestCategoriaRepository:
    """Testes específicos do repositório de categorias."""

    def test_listar_por_tipo_despesa(self, sessao, categoria_alimentacao, categoria_salario):
        repo = CategoriaRepository(sessao)
        despesas = repo.listar_por_tipo("despesa")
        assert len(despesas) == 1
        assert despesas[0].nome == "Alimentação"

    def test_listar_por_tipo_receita(self, sessao, categoria_alimentacao, categoria_salario):
        repo = CategoriaRepository(sessao)
        receitas = repo.listar_por_tipo("receita")
        assert len(receitas) == 1
        assert receitas[0].nome == "Salário"

    def test_buscar_por_nome(self, sessao, categoria_alimentacao):
        repo = CategoriaRepository(sessao)
        cat = repo.buscar_por_nome("Alimentação")
        assert cat is not None
        assert cat.id == categoria_alimentacao.id

    def test_buscar_por_nome_inexistente(self, sessao):
        repo = CategoriaRepository(sessao)
        cat = repo.buscar_por_nome("Inexistente")
        assert cat is None


class TestTransacaoRepository:
    """Testes específicos do repositório de transações."""

    def test_calcular_saldo_sem_transacoes(self, sessao, conta_corrente):
        repo = TransacaoRepository(sessao)
        saldo = repo.calcular_saldo_conta(conta_corrente.id)
        assert saldo == Decimal("2000.00")

    def test_totais_por_tipo_mes_vazio(self, sessao):
        repo = TransacaoRepository(sessao)
        totais = repo.totais_por_tipo_mes(1, 2000)
        assert totais["receita"] == Decimal("0")
        assert totais["despesa"] == Decimal("0")

    def test_listar_por_mes_ano(
        self, sessao, conta_corrente, transacao_receita, transacao_despesa
    ):
        repo = TransacaoRepository(sessao)
        transacoes = repo.listar_por_mes_ano(4, 2025)
        assert len(transacoes) == 2

    def test_listar_por_mes_ano_vazio(self, sessao):
        repo = TransacaoRepository(sessao)
        transacoes = repo.listar_por_mes_ano(1, 2000)
        assert transacoes == []

    def test_gastos_por_categoria(
        self, sessao, conta_corrente, transacao_despesa
    ):
        repo = TransacaoRepository(sessao)
        gastos = repo.gastos_por_categoria(4, 2025)
        assert len(gastos) == 1
        nome, icone, cor, total = gastos[0]
        assert nome == "Alimentação"
        assert float(total) == 350.0
