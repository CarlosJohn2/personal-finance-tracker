"""Comandos CLI para gerenciamento de transações."""
from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from src.cli.ui.prompts import prompt_confirmar, prompt_nova_transacao
from src.cli.ui.tabelas import tabela_transacoes
from src.database.conexao import obter_sessao
from src.repositories.categoria_repo import CategoriaRepository
from src.repositories.conta_repo import ContaRepository
from src.services.transacao_service import TransacaoService

app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
console = Console()


@app.command("adicionar")
def adicionar_transacao() -> None:
    """📝 Adiciona uma nova transação de forma interativa."""
    with obter_sessao() as sessao:
        conta_repo = ContaRepository(sessao)
        cat_repo = CategoriaRepository(sessao)

        contas = conta_repo.listar_ordenado()
        if not contas:
            console.print("[red]Nenhuma conta cadastrada. Adicione uma conta primeiro.[/red]")
            raise typer.Exit(1)

        categorias = cat_repo.listar_ordenado()
        dados = prompt_nova_transacao(contas, categorias)

        if dados is None:
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        svc = TransacaoService(sessao)
        try:
            t = svc.adicionar(**dados)
            console.print(
                f"\n[green]✅ Transação #{t.id} registrada com sucesso![/green]"
            )
        except ValueError as e:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)


@app.command("listar")
def listar_transacoes(
    mes: Optional[int] = typer.Option(None, "--mes", "-m", help="Mês (1–12)"),
    ano: Optional[int] = typer.Option(None, "--ano", "-a", help="Ano (ex: 2025)"),
    limite: int = typer.Option(50, "--limite", "-l", help="Máximo de registros"),
) -> None:
    """📋 Lista transações recentes ou filtradas por mês/ano."""
    from datetime import date as _date

    with obter_sessao() as sessao:
        svc = TransacaoService(sessao)

        if mes and ano:
            transacoes = svc.listar_por_mes(mes, ano)
            console.print(f"\n[dim]Transações de {mes:02d}/{ano}[/dim]")
        elif mes:
            ano = ano or _date.today().year
            transacoes = svc.listar_por_mes(mes, ano)
        else:
            transacoes = svc.listar(limite=limite)

    if not transacoes:
        console.print("[yellow]Nenhuma transação encontrada.[/yellow]")
        return

    console.print()
    console.print(tabela_transacoes(transacoes))
    console.print(f"\n[dim]{len(transacoes)} transação(ões) encontrada(s).[/dim]\n")


@app.command("deletar")
def deletar_transacao(
    id: int = typer.Argument(..., help="ID da transação a remover"),
) -> None:
    """🗑️  Remove uma transação pelo ID."""
    with obter_sessao() as sessao:
        svc = TransacaoService(sessao)
        t = svc.obter(id)

        if not t:
            console.print(f"[red]Transação #{id} não encontrada.[/red]")
            raise typer.Exit(1)

        console.print(
            f"\n[yellow]Transação:[/yellow] #{t.id} — {t.descricao} — "
            f"R$ {t.valor:,.2f} ({t.data.strftime('%d/%m/%Y')})"
        )

        if not prompt_confirmar("Confirma a remoção?"):
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        try:
            svc.remover(id)
            console.print(f"[green]✅ Transação #{id} removida.[/green]")
        except ValueError as e:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)
