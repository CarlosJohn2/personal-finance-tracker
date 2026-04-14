"""Comandos CLI para gerenciamento de metas financeiras."""
from __future__ import annotations

import typer
from rich.console import Console
from rich.rule import Rule

from src.cli.ui.prompts import prompt_aporte_meta, prompt_confirmar, prompt_nova_meta
from src.cli.ui.tabelas import tabela_metas
from src.database.conexao import obter_sessao
from src.services.meta_service import MetaService

app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
console = Console()


@app.command("listar")
def listar_metas(
    todas: bool = typer.Option(False, "--todas", "-t", help="Inclui metas encerradas"),
) -> None:
    """🎯 Lista metas financeiras com progresso."""
    with obter_sessao() as sessao:
        svc = MetaService(sessao)
        metas = svc.listar_todas() if todas else svc.listar_ativas()
        alertas = svc.verificar_alertas()

    if not metas:
        console.print("[yellow]Nenhuma meta cadastrada.[/yellow]")
        return

    console.print()
    console.print(tabela_metas(metas))

    if alertas:
        console.print()
        console.print(Rule("[yellow]🔔 Alertas[/yellow]", style="yellow"))
        for alerta in alertas:
            console.print(f" {alerta}")

    console.print()


@app.command("adicionar")
def adicionar_meta() -> None:
    """➕ Cria uma nova meta financeira."""
    dados = prompt_nova_meta()

    if dados is None:
        console.print("[yellow]Operação cancelada.[/yellow]")
        return

    with obter_sessao() as sessao:
        svc = MetaService(sessao)
        try:
            meta = svc.criar(**dados)
            console.print(
                f"\n[green]✅ Meta '{meta.nome}' criada! "
                f"Alvo: R$ {meta.valor_alvo:,.2f}[/green]"
            )
        except ValueError as e:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)


@app.command("depositar")
def depositar_meta(
    id: int = typer.Argument(..., help="ID da meta"),
) -> None:
    """💰 Registra um aporte em uma meta."""
    with obter_sessao() as sessao:
        svc = MetaService(sessao)
        meta = svc.obter(id)

        if not meta:
            console.print(f"[red]Meta #{id} não encontrada.[/red]")
            raise typer.Exit(1)

        console.print(
            f"\n[cyan]Meta:[/cyan] {meta.nome} — "
            f"Progresso: R$ {meta.valor_atual:,.2f} / R$ {meta.valor_alvo:,.2f} "
            f"({meta.percentual:.1f}%)"
        )

        valor = prompt_aporte_meta()
        if valor is None:
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        try:
            meta_atualizada = svc.depositar(id, valor)
            console.print(
                f"\n[green]✅ Aporte de R$ {valor:,.2f} registrado![/green]\n"
                f"   Progresso: R$ {meta_atualizada.valor_atual:,.2f} / "
                f"R$ {meta_atualizada.valor_alvo:,.2f} "
                f"({meta_atualizada.percentual:.1f}%)"
            )
            if meta_atualizada.concluida:
                console.print("\n[bold green]🎉 Parabéns! Meta atingida![/bold green]")
        except ValueError as e:
            console.print(f"[red]Erro: {e}[/red]")
            raise typer.Exit(1)


@app.command("encerrar")
def encerrar_meta(
    id: int = typer.Argument(..., help="ID da meta a encerrar"),
) -> None:
    """🔒 Encerra uma meta (marca como inativa)."""
    with obter_sessao() as sessao:
        svc = MetaService(sessao)
        meta = svc.obter(id)

        if not meta:
            console.print(f"[red]Meta #{id} não encontrada.[/red]")
            raise typer.Exit(1)

        console.print(
            f"\n[yellow]Meta:[/yellow] #{meta.id} — {meta.nome} "
            f"({meta.percentual:.1f}% concluída)"
        )

        if not prompt_confirmar("Confirma o encerramento?"):
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        svc.encerrar(id)
        console.print(f"[green]✅ Meta '{meta.nome}' encerrada.[/green]")
