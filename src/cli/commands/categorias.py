"""Comandos CLI para gerenciamento de categorias."""
from __future__ import annotations

import typer
from rich.console import Console

from src.cli.ui.prompts import prompt_confirmar, prompt_nova_categoria
from src.cli.ui.tabelas import tabela_categorias
from src.database.conexao import obter_sessao
from src.repositories.categoria_repo import CategoriaRepository

app = typer.Typer(rich_markup_mode="rich", no_args_is_help=True)
console = Console()


@app.command("listar")
def listar_categorias(
    tipo: str = typer.Option("", "--tipo", "-t", help="Filtrar por 'receita' ou 'despesa'"),
) -> None:
    """🏷️  Lista todas as categorias cadastradas."""
    with obter_sessao() as sessao:
        repo = CategoriaRepository(sessao)

        if tipo in ("receita", "despesa"):
            categorias = repo.listar_por_tipo(tipo)
        else:
            categorias = repo.listar_ordenado()

    if not categorias:
        console.print("[yellow]Nenhuma categoria cadastrada.[/yellow]")
        return

    console.print()
    console.print(tabela_categorias(categorias))
    console.print(f"\n[dim]{len(categorias)} categoria(s) encontrada(s).[/dim]\n")


@app.command("adicionar")
def adicionar_categoria() -> None:
    """➕ Adiciona uma nova categoria de forma interativa."""
    with obter_sessao() as sessao:
        repo = CategoriaRepository(sessao)
        dados = prompt_nova_categoria()

        if dados is None:
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        existente = repo.buscar_por_nome(dados["nome"])
        if existente:
            console.print(
                f"[red]Já existe uma categoria com o nome '{dados['nome']}'.[/red]"
            )
            raise typer.Exit(1)

        cat = repo.criar(**dados)
        console.print(
            f"\n[green]✅ Categoria '{cat.icone} {cat.nome}' criada (ID: {cat.id}).[/green]"
        )


@app.command("deletar")
def deletar_categoria(
    id: int = typer.Argument(..., help="ID da categoria a remover"),
) -> None:
    """🗑️  Remove uma categoria pelo ID."""
    with obter_sessao() as sessao:
        repo = CategoriaRepository(sessao)
        cat = repo.obter(id)

        if not cat:
            console.print(f"[red]Categoria #{id} não encontrada.[/red]")
            raise typer.Exit(1)

        if cat.transacoes:
            console.print(
                f"[red]Não é possível remover: a categoria '{cat.nome}' "
                f"possui {len(cat.transacoes)} transação(ões) vinculada(s).[/red]"
            )
            raise typer.Exit(1)

        console.print(f"\n[yellow]Categoria:[/yellow] #{cat.id} — {cat.icone} {cat.nome}")

        if not prompt_confirmar("Confirma a remoção?"):
            console.print("[yellow]Operação cancelada.[/yellow]")
            return

        repo.deletar(id)
        console.print(f"[green]✅ Categoria '{cat.nome}' removida.[/green]")
