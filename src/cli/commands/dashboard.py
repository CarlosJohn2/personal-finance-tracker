"""Comando de dashboard — visão geral das finanças."""
from __future__ import annotations

from datetime import date
from decimal import Decimal

import typer
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich import box

from src.cli.ui.paineis import (
    cabecalho_app,
    painel_alertas,
    painel_categorias_top,
    painel_resumo_mes,
    painel_saldo,
    painel_transacoes_recentes,
)
from src.cli.ui.tabelas import tabela_contas
from src.database.conexao import obter_sessao
from src.repositories.conta_repo import ContaRepository
from src.services.meta_service import MetaService
from src.services.relatorio_service import RelatorioService
from src.services.transacao_service import TransacaoService

console = Console()


def exibir_dashboard() -> None:
    """Exibe o dashboard financeiro completo no terminal."""
    hoje = date.today()
    mes, ano = hoje.month, hoje.year

    with obter_sessao() as sessao:
        transacao_svc = TransacaoService(sessao)
        relatorio_svc = RelatorioService(sessao)
        meta_svc = MetaService(sessao)
        conta_repo = ContaRepository(sessao)

        saldo_total = transacao_svc.saldo_total()
        resumo = relatorio_svc.resumo_mensal(mes, ano)
        transacoes_recentes = transacao_svc.listar(limite=5)
        alertas = meta_svc.verificar_alertas()
        contas = conta_repo.listar_ordenado()
        saldos = {c.id: transacao_svc.saldo_conta(c.id) for c in contas}

    cabecalho_app()

    # ── Linha 1: Saldo + Resumo do mês ────────────────────────────────
    console.print(
        Columns(
            [
                painel_saldo(saldo_total),
                painel_resumo_mes(resumo),
            ],
            equal=True,
            expand=True,
        )
    )

    # ── Linha 2: Contas ───────────────────────────────────────────────
    if contas:
        console.print(tabela_contas(contas, saldos))

    # ── Linha 3: Transações Recentes + Top Gastos ─────────────────────
    console.print(
        Columns(
            [
                painel_transacoes_recentes(transacoes_recentes),
                painel_categorias_top(resumo["categorias"]),
            ],
            equal=True,
            expand=True,
        )
    )

    # ── Linha 4: Alertas de metas ─────────────────────────────────────
    if alertas:
        console.print(painel_alertas(alertas))

    console.print()
    console.print(
        Rule(
            "[dim]Use [bold]financa --help[/bold] para ver todos os comandos[/dim]",
            style="bright_black",
        )
    )
    console.print()
