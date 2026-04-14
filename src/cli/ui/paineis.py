"""Componentes Rich de painéis e layouts para o dashboard."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Dict, List

from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from src.cli.ui.tabelas import _barra_progresso

console = Console()


def painel_saldo(saldo: Decimal, label: str = "Saldo Total") -> Panel:
    """Cria painel com saldo em destaque.

    Args:
        saldo: Valor do saldo.
        label: Rótulo do painel.

    Returns:
        Panel: Painel Rich formatado.
    """
    sinal = "+" if saldo >= 0 else ""
    cor = "bold green" if saldo >= 0 else "bold red"
    icone = "📈" if saldo >= 0 else "📉"

    conteudo = Align.center(
        Text(f"{icone}  {sinal}R$ {saldo:,.2f}", style=cor, justify="center"),
        vertical="middle",
    )

    return Panel(
        conteudo,
        title=f"[bold cyan]{label}[/bold cyan]",
        border_style="cyan",
        box=box.DOUBLE_EDGE,
        height=5,
        padding=(1, 2),
    )


def painel_resumo_mes(resumo: Dict) -> Panel:
    """Cria painel com resumo financeiro do mês.

    Args:
        resumo: Dicionário retornado por RelatorioService.resumo_mensal().

    Returns:
        Panel: Painel Rich com receitas, despesas e saldo.
    """
    receita = resumo["receita"]
    despesa = resumo["despesa"]
    saldo = resumo["saldo"]
    nome_mes = resumo["nome_mes"]
    ano = resumo["ano"]
    total_t = resumo["total_transacoes"]

    cor_saldo = "green" if saldo >= 0 else "red"
    sinal = "+" if saldo >= 0 else ""

    linhas = (
        f"[green]  Receitas   R$ {receita:>12,.2f}[/green]\n"
        f"[red]  Despesas   R$ {despesa:>12,.2f}[/red]\n"
        f"[bright_black]{'─' * 28}[/bright_black]\n"
        f"[{cor_saldo}]  Saldo      {sinal}R$ {saldo:>11,.2f}[/{cor_saldo}]\n\n"
        f"[dim]  {total_t} transações em {nome_mes}/{ano}[/dim]"
    )

    return Panel(
        linhas,
        title=f"[bold cyan]📅 {nome_mes}/{ano}[/bold cyan]",
        border_style="bright_black",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def painel_categorias_top(categorias: List, limite: int = 5) -> Panel:
    """Cria painel com ranking de gastos por categoria.

    Args:
        categorias: Lista de (nome, icone, cor, total) de despesas.
        limite: Máximo de categorias exibidas.

    Returns:
        Panel: Painel Rich com ranking.
    """
    if not categorias:
        return Panel(
            "[dim]Nenhuma despesa registrada neste mês.[/dim]",
            title="[bold cyan]💸 Top Gastos[/bold cyan]",
            border_style="bright_black",
            box=box.ROUNDED,
        )

    total_geral = sum(t for _, _, _, t in categorias) or Decimal("1")
    linhas = []

    for i, (nome, icone, _, valor) in enumerate(categorias[:limite], 1):
        pct = float(valor / total_geral * 100)
        barra = _barra_progresso(pct, largura=12)
        linhas.append(
            f" {i}. {icone} {nome:<18} R$ {valor:>9,.2f}  {barra} {pct:.0f}%"
        )

    return Panel(
        "\n".join(linhas),
        title="[bold cyan]💸 Top Gastos por Categoria[/bold cyan]",
        border_style="bright_black",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def painel_alertas(alertas: List[str]) -> Panel:
    """Cria painel com alertas de metas.

    Args:
        alertas: Lista de strings de alerta.

    Returns:
        Panel: Painel Rich com alertas ou mensagem vazia.
    """
    if not alertas:
        conteudo = "[dim]Nenhum alerta no momento.[/dim]"
    else:
        conteudo = "\n".join(f" {alerta}" for alerta in alertas)

    return Panel(
        conteudo,
        title="[bold yellow]🔔 Alertas de Metas[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def painel_transacoes_recentes(transacoes: list, limite: int = 5) -> Panel:
    """Cria painel com as últimas transações.

    Args:
        transacoes: Lista de transações ordenadas por data desc.
        limite: Número de transações a exibir.

    Returns:
        Panel: Painel Rich com transações recentes.
    """
    if not transacoes:
        return Panel(
            "[dim]Nenhuma transação registrada.[/dim]",
            title="[bold cyan]🕐 Transações Recentes[/bold cyan]",
            border_style="bright_black",
            box=box.ROUNDED,
        )

    linhas = []
    for t in transacoes[:limite]:
        cor = "green" if t.tipo == "receita" else "red"
        sinal = "+" if t.tipo == "receita" else "-"
        cat = f"{t.categoria.icone} " if t.categoria else ""
        linhas.append(
            f" [dim]{t.data.strftime('%d/%m')}[/dim]  "
            f"{cat}{t.descricao[:28]:<30}"
            f"[{cor}]{sinal}R$ {t.valor:>9,.2f}[/{cor}]"
        )

    return Panel(
        "\n".join(linhas),
        title="[bold cyan]🕐 Transações Recentes[/bold cyan]",
        border_style="bright_black",
        box=box.ROUNDED,
        padding=(0, 1),
    )


def cabecalho_app() -> None:
    """Exibe o cabeçalho principal da aplicação."""
    hoje = date.today()
    titulo = Text()
    titulo.append("  💰 Personal Finance Tracker  ", style="bold white on dark_green")

    console.print()
    console.print(Align.center(titulo))
    console.print(
        Align.center(
            f"[dim]Hoje: {hoje.strftime('%A, %d de %B de %Y')}[/dim]"
        )
    )
    console.print()
