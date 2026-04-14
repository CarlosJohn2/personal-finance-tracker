"""Componentes Rich de tabelas para exibição de dados."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import List

from rich.table import Table
from rich import box

from src.models.categoria import Categoria
from src.models.conta import Conta
from src.models.meta import Meta
from src.models.transacao import Transacao


def _cor_valor(valor: Decimal, tipo: str) -> str:
    """Retorna a cor Rich baseada no tipo de transação."""
    return "green" if tipo == "receita" else "red"


def tabela_transacoes(transacoes: List[Transacao]) -> Table:
    """Constrói tabela Rich de transações.

    Args:
        transacoes: Lista de transações a exibir.

    Returns:
        Table: Tabela Rich formatada.
    """
    tabela = Table(
        title="📝 Transações",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        show_lines=False,
        expand=True,
    )

    tabela.add_column("ID", style="dim", width=5, justify="right")
    tabela.add_column("Data", width=12, justify="center")
    tabela.add_column("Descrição", min_width=25)
    tabela.add_column("Categoria", width=20)
    tabela.add_column("Conta", width=15)
    tabela.add_column("Tipo", width=9, justify="center")
    tabela.add_column("Valor", width=14, justify="right")

    for t in transacoes:
        cor = _cor_valor(t.valor, t.tipo)
        cat_str = (
            f"{t.categoria.icone} {t.categoria.nome}" if t.categoria else "[dim]—[/dim]"
        )
        conta_str = t.conta.nome if t.conta else "—"
        tipo_badge = (
            "[green]● Receita[/green]" if t.tipo == "receita"
            else "[red]● Despesa[/red]"
        )
        sinal = "+" if t.tipo == "receita" else "-"

        tabela.add_row(
            str(t.id),
            t.data.strftime("%d/%m/%Y"),
            t.descricao,
            cat_str,
            conta_str,
            tipo_badge,
            f"[{cor}]{sinal} R$ {t.valor:,.2f}[/{cor}]",
        )

    return tabela


def tabela_categorias(categorias: List[Categoria]) -> Table:
    """Constrói tabela Rich de categorias.

    Args:
        categorias: Lista de categorias a exibir.

    Returns:
        Table: Tabela Rich formatada.
    """
    tabela = Table(
        title="🏷️  Categorias",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        expand=False,
    )

    tabela.add_column("ID", style="dim", width=5, justify="right")
    tabela.add_column("Ícone", width=5, justify="center")
    tabela.add_column("Nome", min_width=20)
    tabela.add_column("Tipo", width=10, justify="center")
    tabela.add_column("Cor", width=10, justify="center")

    for cat in categorias:
        tipo_fmt = (
            "[green]Receita[/green]" if cat.tipo == "receita"
            else "[red]Despesa[/red]"
        )
        tabela.add_row(
            str(cat.id),
            cat.icone,
            cat.nome,
            tipo_fmt,
            cat.cor,
        )

    return tabela


def tabela_contas(contas: List[Conta], saldos: dict) -> Table:
    """Constrói tabela Rich de contas com saldos.

    Args:
        contas: Lista de contas.
        saldos: Dicionário {conta_id: saldo}.

    Returns:
        Table: Tabela Rich formatada.
    """
    tabela = Table(
        title="🏦 Contas",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        expand=False,
    )

    tabela.add_column("ID", style="dim", width=5, justify="right")
    tabela.add_column("", width=3, justify="center")
    tabela.add_column("Nome", min_width=20)
    tabela.add_column("Tipo", width=14, justify="center")
    tabela.add_column("Saldo Inicial", width=14, justify="right")
    tabela.add_column("Saldo Atual", width=14, justify="right")

    for conta in contas:
        saldo = saldos.get(conta.id, Decimal("0"))
        cor_saldo = "green" if saldo >= 0 else "red"

        tabela.add_row(
            str(conta.id),
            conta.icone,
            conta.nome,
            conta.tipo.capitalize(),
            f"R$ {conta.saldo_inicial:,.2f}",
            f"[{cor_saldo}]R$ {saldo:,.2f}[/{cor_saldo}]",
        )

    return tabela


def tabela_metas(metas: List[Meta]) -> Table:
    """Constrói tabela Rich de metas com barras de progresso.

    Args:
        metas: Lista de metas a exibir.

    Returns:
        Table: Tabela Rich formatada.
    """
    tabela = Table(
        title="🎯 Metas Financeiras",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        expand=True,
    )

    tabela.add_column("ID", style="dim", width=5, justify="right")
    tabela.add_column("Nome", min_width=18)
    tabela.add_column("Alvo", width=13, justify="right")
    tabela.add_column("Atual", width=13, justify="right")
    tabela.add_column("Restante", width=13, justify="right")
    tabela.add_column("Progresso", min_width=24)
    tabela.add_column("Prazo", width=12, justify="center")
    tabela.add_column("Status", width=10, justify="center")

    for meta in metas:
        pct = meta.percentual
        barra = _barra_progresso(pct)

        prazo_str = (
            meta.data_limite.strftime("%d/%m/%Y") if meta.data_limite else "[dim]—[/dim]"
        )

        if meta.concluida:
            status = "[green]✅ Pronta[/green]"
        elif not meta.ativa:
            status = "[dim]Encerrada[/dim]"
        else:
            status = "[yellow]Em andamento[/yellow]"

        tabela.add_row(
            str(meta.id),
            meta.nome,
            f"R$ {meta.valor_alvo:,.2f}",
            f"R$ {meta.valor_atual:,.2f}",
            f"[yellow]R$ {meta.restante:,.2f}[/yellow]",
            f"{barra} [dim]{pct:.1f}%[/dim]",
            prazo_str,
            status,
        )

    return tabela


def _barra_progresso(pct: float, largura: int = 16) -> str:
    """Gera uma barra de progresso em texto usando blocos Unicode.

    Args:
        pct: Percentual (0–100).
        largura: Número de blocos da barra.

    Returns:
        str: String formatada com Rich markup.
    """
    preenchido = int(pct / 100 * largura)
    vazio = largura - preenchido

    if pct >= 100:
        cor = "green"
    elif pct >= 60:
        cor = "yellow"
    else:
        cor = "red"

    return f"[{cor}]{'█' * preenchido}[/{cor}][dim]{'░' * vazio}[/dim]"
