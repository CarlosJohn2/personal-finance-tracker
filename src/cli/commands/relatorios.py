"""Comandos CLI para geração de relatórios e exportação."""
from __future__ import annotations

from datetime import date

import typer
from rich.console import Console
from rich.rule import Rule
from rich.table import Table
from rich import box

from src.cli.ui.paineis import painel_categorias_top, painel_resumo_mes
from src.database.conexao import obter_sessao
from src.services.exportacao_service import ExportacaoService
from src.services.relatorio_service import MESES_PT, RelatorioService

app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
console = Console()


@app.command("mensal")
def relatorio_mensal(
    mes: int = typer.Option(date.today().month, "--mes", "-m", help="Mês (1–12)"),
    ano: int = typer.Option(date.today().year, "--ano", "-a", help="Ano"),
    grafico: bool = typer.Option(False, "--grafico", "-g", help="Gerar gráfico de pizza"),
) -> None:
    """📊 Exibe o relatório financeiro de um mês."""
    with obter_sessao() as sessao:
        svc = RelatorioService(sessao)
        resumo = svc.resumo_mensal(mes, ano)

        console.print()
        console.print(Rule(f"[bold cyan]📅 Relatório — {MESES_PT[mes]}/{ano}[/bold cyan]"))
        console.print()
        console.print(painel_resumo_mes(resumo))
        console.print(painel_categorias_top(resumo["categorias"]))

        if grafico:
            try:
                caminho = svc.gerar_grafico_pizza(mes, ano)
                console.print(f"\n[green]📈 Gráfico salvo em:[/green] {caminho}")
            except ValueError as e:
                console.print(f"[yellow]⚠️  {e}[/yellow]")

        console.print()


@app.command("anual")
def relatorio_anual(
    ano: int = typer.Option(date.today().year, "--ano", "-a", help="Ano"),
    grafico: bool = typer.Option(False, "--grafico", "-g", help="Gerar gráfico anual"),
) -> None:
    """📅 Exibe o histórico financeiro anual."""
    with obter_sessao() as sessao:
        svc = RelatorioService(sessao)
        historico = svc.historico_anual(ano)

    console.print()
    console.print(Rule(f"[bold cyan]📅 Histórico Anual — {ano}[/bold cyan]"))
    console.print()

    tabela = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        expand=False,
    )
    tabela.add_column("Mês", width=12)
    tabela.add_column("Receitas", width=15, justify="right")
    tabela.add_column("Despesas", width=15, justify="right")
    tabela.add_column("Saldo", width=15, justify="right")
    tabela.add_column("Balanço", width=22)

    total_r = historico["total_receita"]
    total_d = historico["total_despesa"]

    for m in range(1, 13):
        dados = historico["meses"][m]
        r, d = dados["receita"], dados["despesa"]
        saldo = r - d
        cor = "green" if saldo >= 0 else "red"
        sinal = "+" if saldo >= 0 else ""

        from src.cli.ui.tabelas import _barra_progresso
        max_val = max(float(total_r) / 12, 1)
        barra = _barra_progresso(float(r) / max_val * 100, largura=14) if r > 0 else "[dim]" + "░" * 14 + "[/dim]"

        tabela.add_row(
            MESES_PT[m],
            f"[green]R$ {r:,.2f}[/green]",
            f"[red]R$ {d:,.2f}[/red]",
            f"[{cor}]{sinal}R$ {saldo:,.2f}[/{cor}]",
            barra,
        )

    saldo_anual = historico["saldo_anual"]
    cor_total = "green" if saldo_anual >= 0 else "red"
    sinal_total = "+" if saldo_anual >= 0 else ""

    tabela.add_section()
    tabela.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold green]R$ {total_r:,.2f}[/bold green]",
        f"[bold red]R$ {total_d:,.2f}[/bold red]",
        f"[bold {cor_total}]{sinal_total}R$ {saldo_anual:,.2f}[/bold {cor_total}]",
        "",
    )

    console.print(tabela)

    if grafico:
        with obter_sessao() as sessao:
            svc = RelatorioService(sessao)
            try:
                caminho = svc.gerar_grafico_anual(ano)
                console.print(f"\n[green]📈 Gráfico salvo em:[/green] {caminho}")
            except Exception as e:
                console.print(f"[yellow]⚠️  Erro ao gerar gráfico: {e}[/yellow]")

    console.print()


@app.command("exportar")
def exportar(
    mes: int = typer.Option(date.today().month, "--mes", "-m", help="Mês (1–12)"),
    ano: int = typer.Option(date.today().year, "--ano", "-a", help="Ano"),
    formato: str = typer.Option("csv", "--formato", "-f", help="Formato: 'csv' ou 'pdf'"),
) -> None:
    """💾 Exporta o relatório do mês para CSV ou PDF."""
    formato = formato.lower()
    if formato not in ("csv", "pdf"):
        console.print("[red]Formato inválido. Use 'csv' ou 'pdf'.[/red]")
        raise typer.Exit(1)

    with obter_sessao() as sessao:
        svc = ExportacaoService(sessao)
        try:
            if formato == "csv":
                caminho = svc.exportar_csv(mes, ano)
                console.print(f"\n[green]✅ CSV exportado:[/green] {caminho}")
            else:
                caminho = svc.exportar_pdf(mes, ano)
                console.print(f"\n[green]✅ PDF exportado:[/green] {caminho}")
        except Exception as e:
            console.print(f"[red]Erro na exportação: {e}[/red]")
            raise typer.Exit(1)
