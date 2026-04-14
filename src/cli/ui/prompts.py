"""Prompts interativos para entrada de dados no terminal."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Optional, Tuple

import questionary
from questionary import Style

from src.models.categoria import Categoria
from src.models.conta import Conta

ESTILO_QUESTIONARY = Style([
    ("qmark", "fg:#00ff88 bold"),
    ("question", "bold"),
    ("answer", "fg:#00ff88"),
    ("pointer", "fg:#00ff88 bold"),
    ("highlighted", "fg:#00ff88 bold"),
    ("selected", "fg:#00ff88"),
    ("separator", "fg:#444444"),
    ("instruction", "fg:#888888"),
])


def _validar_valor(texto: str) -> bool | str:
    """Validador de valor monetário para questionary."""
    try:
        v = Decimal(texto.replace(",", "."))
        if v <= 0:
            return "O valor deve ser maior que zero."
        return True
    except InvalidOperation:
        return "Digite um número válido (ex: 1500.00)."


def _validar_data(texto: str) -> bool | str:
    """Validador de data no formato DD/MM/AAAA."""
    try:
        datetime.strptime(texto, "%d/%m/%Y")
        return True
    except ValueError:
        return "Use o formato DD/MM/AAAA."


def prompt_nova_transacao(
    contas: List[Conta],
    categorias: List[Categoria],
) -> Optional[dict]:
    """Coleta dados de uma nova transação via prompts interativos.

    Args:
        contas: Lista de contas disponíveis.
        categorias: Lista de categorias disponíveis.

    Returns:
        Optional[dict]: Dados da transação ou None se cancelado.
    """
    tipo = questionary.select(
        "Tipo de transação:",
        choices=[
            questionary.Choice("💹 Receita", value="receita"),
            questionary.Choice("💸 Despesa", value="despesa"),
        ],
        style=ESTILO_QUESTIONARY,
    ).ask()

    if tipo is None:
        return None

    descricao = questionary.text(
        "Descrição:",
        validate=lambda t: True if t.strip() else "A descrição não pode ser vazia.",
        style=ESTILO_QUESTIONARY,
    ).ask()

    if descricao is None:
        return None

    valor_str = questionary.text(
        "Valor (R$):",
        validate=_validar_valor,
        style=ESTILO_QUESTIONARY,
    ).ask()

    if valor_str is None:
        return None

    data_str = questionary.text(
        "Data (DD/MM/AAAA):",
        default=date.today().strftime("%d/%m/%Y"),
        validate=_validar_data,
        style=ESTILO_QUESTIONARY,
    ).ask()

    if data_str is None:
        return None

    opcoes_conta = [
        questionary.Choice(f"{c.icone} {c.nome}", value=c.id) for c in contas
    ]
    conta_id = questionary.select(
        "Conta:",
        choices=opcoes_conta,
        style=ESTILO_QUESTIONARY,
    ).ask()

    if conta_id is None:
        return None

    cats_tipo = [c for c in categorias if c.tipo == tipo]
    opcoes_cat = [
        questionary.Choice("— Sem categoria", value=None),
        *[questionary.Choice(f"{c.icone} {c.nome}", value=c.id) for c in cats_tipo],
    ]
    categoria_id = questionary.select(
        "Categoria:",
        choices=opcoes_cat,
        style=ESTILO_QUESTIONARY,
    ).ask()

    observacao = questionary.text(
        "Observação (opcional):",
        style=ESTILO_QUESTIONARY,
    ).ask()

    return {
        "tipo": tipo,
        "descricao": descricao.strip(),
        "valor": Decimal(valor_str.replace(",", ".")),
        "data": datetime.strptime(data_str, "%d/%m/%Y").date(),
        "conta_id": conta_id,
        "categoria_id": categoria_id,
        "observacao": observacao.strip() if observacao and observacao.strip() else None,
    }


def prompt_nova_categoria() -> Optional[dict]:
    """Coleta dados de uma nova categoria via prompts interativos.

    Returns:
        Optional[dict]: Dados da categoria ou None se cancelado.
    """
    nome = questionary.text(
        "Nome da categoria:",
        validate=lambda t: True if t.strip() else "Nome não pode ser vazio.",
        style=ESTILO_QUESTIONARY,
    ).ask()
    if nome is None:
        return None

    tipo = questionary.select(
        "Tipo:",
        choices=[
            questionary.Choice("💹 Receita", value="receita"),
            questionary.Choice("💸 Despesa", value="despesa"),
        ],
        style=ESTILO_QUESTIONARY,
    ).ask()
    if tipo is None:
        return None

    icone = questionary.text(
        "Ícone (emoji):",
        default="💰",
        validate=lambda t: True if t.strip() else "Insira um emoji.",
        style=ESTILO_QUESTIONARY,
    ).ask()
    if icone is None:
        return None

    cor = questionary.text(
        "Cor hexadecimal (ex: #ff5555):",
        default="#00ff88",
        validate=lambda t: True if (len(t) == 7 and t.startswith("#")) else "Use formato #rrggbb.",
        style=ESTILO_QUESTIONARY,
    ).ask()
    if cor is None:
        return None

    return {
        "nome": nome.strip(),
        "tipo": tipo,
        "icone": icone.strip(),
        "cor": cor.strip(),
    }


def prompt_nova_meta() -> Optional[dict]:
    """Coleta dados de uma nova meta financeira.

    Returns:
        Optional[dict]: Dados da meta ou None se cancelado.
    """
    nome = questionary.text(
        "Nome da meta:",
        validate=lambda t: True if t.strip() else "Nome não pode ser vazio.",
        style=ESTILO_QUESTIONARY,
    ).ask()
    if nome is None:
        return None

    valor_str = questionary.text(
        "Valor alvo (R$):",
        validate=_validar_valor,
        style=ESTILO_QUESTIONARY,
    ).ask()
    if valor_str is None:
        return None

    usar_prazo = questionary.confirm(
        "Definir prazo?", default=False, style=ESTILO_QUESTIONARY
    ).ask()

    data_limite = None
    if usar_prazo:
        data_str = questionary.text(
            "Prazo (DD/MM/AAAA):",
            validate=_validar_data,
            style=ESTILO_QUESTIONARY,
        ).ask()
        if data_str:
            data_limite = datetime.strptime(data_str, "%d/%m/%Y").date()

    return {
        "nome": nome.strip(),
        "valor_alvo": Decimal(valor_str.replace(",", ".")),
        "data_limite": data_limite,
    }


def prompt_confirmar(mensagem: str) -> bool:
    """Exibe prompt de confirmação.

    Args:
        mensagem: Texto da confirmação.

    Returns:
        bool: True se confirmado.
    """
    return questionary.confirm(
        mensagem, default=False, style=ESTILO_QUESTIONARY
    ).ask() or False


def prompt_aporte_meta() -> Optional[Decimal]:
    """Solicita valor de aporte para uma meta.

    Returns:
        Optional[Decimal]: Valor digitado ou None.
    """
    valor_str = questionary.text(
        "Valor do aporte (R$):",
        validate=_validar_valor,
        style=ESTILO_QUESTIONARY,
    ).ask()

    if valor_str is None:
        return None
    return Decimal(valor_str.replace(",", "."))
