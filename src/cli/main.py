"""Ponto de entrada principal da CLI — Personal Finance Tracker."""
from __future__ import annotations

import typer
from rich.console import Console

from src.cli.commands import categorias, dashboard, metas, relatorios, transacoes

app = typer.Typer(
    name="financa",
    help="💰 [bold green]Personal Finance Tracker[/bold green] — Controle financeiro pessoal no terminal.",
    rich_markup_mode="rich",
    no_args_is_help=False,
    add_completion=False,
    pretty_exceptions_enable=True,
)

console = Console()

app.add_typer(transacoes.app, name="transacao", help="📝  Gerenciar transações")
app.add_typer(categorias.app, name="categoria", help="🏷️   Gerenciar categorias")
app.add_typer(relatorios.app, name="relatorio", help="📊  Relatórios e gráficos")
app.add_typer(metas.app, name="meta", help="🎯  Metas financeiras")


@app.command("dashboard", hidden=False)
def cmd_dashboard() -> None:
    """🖥️  Exibe o painel financeiro completo."""
    dashboard.exibir_dashboard()


@app.callback(invoke_without_command=True)
def callback(ctx: typer.Context) -> None:
    """💰 Personal Finance Tracker — sem subcomando exibe o dashboard."""
    if ctx.invoked_subcommand is None:
        dashboard.exibir_dashboard()


def main() -> None:
    """Entry point instalado via pyproject.toml."""
    app()


if __name__ == "__main__":
    main()
