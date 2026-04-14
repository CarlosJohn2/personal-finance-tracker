"""Script de seed — popula o banco com dados realistas de 12 meses."""
from __future__ import annotations

import io
import random
import sys
from datetime import date, timedelta
from decimal import Decimal

# Força UTF-8 no Windows para suportar emojis
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.progress import track

from src.database.conexao import obter_sessao
from src.models.base import Base
from src.models.categoria import Categoria
from src.models.conta import Conta
from src.models.meta import Meta
from src.models.transacao import Transacao
from src.database.conexao import engine

console = Console(force_terminal=False, highlight=False)

CATEGORIAS_DESPESA = [
    ("Alimentação", "🍔", "#f38ba8"),
    ("Moradia", "🏠", "#fab387"),
    ("Transporte", "🚗", "#f9e2af"),
    ("Saúde", "💊", "#a6e3a1"),
    ("Educação", "📚", "#89dceb"),
    ("Lazer", "🎮", "#cba6f7"),
    ("Roupas", "👕", "#f2cdcd"),
    ("Restaurantes", "🍽️", "#eba0ac"),
    ("Streaming", "📺", "#89b4fa"),
    ("Pet", "🐾", "#b4befe"),
]

CATEGORIAS_RECEITA = [
    ("Salário", "💼", "#a6e3a1"),
    ("Freelance", "💻", "#89dceb"),
    ("Investimentos", "📈", "#cba6f7"),
    ("Aluguel Recebido", "🏢", "#fab387"),
    ("Outros", "💰", "#f9e2af"),
]

CONTAS = [
    ("Nubank", "corrente", Decimal("1500.00")),
    ("Poupança Caixa", "poupanca", Decimal("8000.00")),
    ("Carteira", "carteira", Decimal("200.00")),
]

METAS = [
    ("Reserva de Emergência", Decimal("20000.00"), Decimal("12000.00"), None),
    ("Viagem para Europa", Decimal("15000.00"), Decimal("4500.00"), date(2026, 7, 1)),
    ("Notebook Novo", Decimal("6000.00"), Decimal("2000.00"), date(2025, 12, 1)),
    ("Carro", Decimal("45000.00"), Decimal("8000.00"), date(2027, 6, 1)),
]

DESCRICOES_DESPESA = {
    "Alimentação": ["Supermercado Extra", "Pão de Açúcar", "Atacadão", "Feira livre"],
    "Moradia": ["Aluguel", "Condomínio", "Conta de luz", "Água e esgoto", "Internet"],
    "Transporte": ["Combustível", "Uber", "Manutenção do carro", "Metrô — recarga"],
    "Saúde": ["Farmácia", "Plano de saúde", "Consulta médica", "Academia"],
    "Educação": ["Udemy", "Curso de inglês", "Livros técnicos", "Alura"],
    "Lazer": ["Cinema", "Show", "PlayStation Store", "Spotify"],
    "Roupas": ["Renner", "Zara", "Shopee — roupas", "C&A"],
    "Restaurantes": ["iFood", "Rodízio japonês", "Outback", "Padaria"],
    "Streaming": ["Netflix", "Disney+", "Amazon Prime", "HBO Max"],
    "Pet": ["Vet", "Ração", "PetSmile", "Banho e tosa"],
}

DESCRICOES_RECEITA = {
    "Salário": ["Salário mensal — empresa XYZ", "Pagamento 13º salário"],
    "Freelance": ["Projeto React — cliente A", "Consultoria — cliente B", "Desenvolvimento API"],
    "Investimentos": ["Dividendos FII", "Rendimento CDB", "Tesouro Direto"],
    "Aluguel Recebido": ["Aluguel apartamento 501"],
    "Outros": ["Reembolso despesa", "Venda — Mercado Livre", "PIX recebido"],
}


def criar_schema():
    console.print("[cyan]Criando schema...[/cyan]")
    Base.metadata.create_all(engine)


def seed_categorias(sessao) -> dict:
    console.print("[cyan]Criando categorias...[/cyan]")
    cats = {}

    for nome, icone, cor in CATEGORIAS_DESPESA:
        cat = Categoria(nome=nome, icone=icone, tipo="despesa", cor=cor)
        sessao.add(cat)
        cats[nome] = cat

    for nome, icone, cor in CATEGORIAS_RECEITA:
        cat = Categoria(nome=nome, icone=icone, tipo="receita", cor=cor)
        sessao.add(cat)
        cats[nome] = cat

    sessao.flush()
    return cats


def seed_contas(sessao) -> list:
    console.print("[cyan]Criando contas...[/cyan]")
    contas = []
    for nome, tipo, saldo in CONTAS:
        conta = Conta(nome=nome, tipo=tipo, saldo_inicial=saldo)
        sessao.add(conta)
        contas.append(conta)
    sessao.flush()
    return contas


def seed_metas(sessao, cats: dict) -> None:
    console.print("[cyan]Criando metas...[/cyan]")
    for nome, alvo, atual, prazo in METAS:
        meta = Meta(
            nome=nome,
            valor_alvo=alvo,
            valor_atual=atual,
            data_limite=prazo,
            ativa=True,
        )
        sessao.add(meta)
    sessao.flush()


def seed_transacoes(sessao, contas: list, cats: dict) -> None:
    console.print("[cyan]Gerando 12 meses de transações...[/cyan]")
    hoje = date.today()
    conta_principal = contas[0]
    conta_poupanca = contas[1]

    transacoes_criadas = 0

    for meses_atras in range(12, -1, -1):
        ano = hoje.year
        mes = hoje.month - meses_atras
        while mes <= 0:
            mes += 12
            ano -= 1

        # Salário — todo dia 5
        dia_salario = min(5, 28)
        salario = round(random.uniform(5500, 7000), 2)
        t = Transacao(
            descricao="Salário mensal — empresa XYZ",
            valor=Decimal(str(salario)),
            tipo="receita",
            data=date(ano, mes, dia_salario),
            conta_id=conta_principal.id,
            categoria_id=cats["Salário"].id,
        )
        sessao.add(t)
        transacoes_criadas += 1

        # Despesas fixas mensais
        despesas_fixas = [
            ("Aluguel", "Moradia", Decimal("1800.00"), 10),
            ("Condomínio", "Moradia", Decimal("350.00"), 10),
            ("Netflix", "Streaming", Decimal("39.90"), 15),
            ("Spotify", "Streaming", Decimal("21.90"), 15),
            ("Academia", "Saúde", Decimal("120.00"), 8),
            ("Plano de saúde", "Saúde", Decimal("280.00"), 5),
            ("Internet", "Moradia", Decimal("119.90"), 10),
        ]

        for desc, cat_nome, valor, dia in despesas_fixas:
            t = Transacao(
                descricao=desc,
                valor=valor,
                tipo="despesa",
                data=date(ano, mes, min(dia, 28)),
                conta_id=conta_principal.id,
                categoria_id=cats[cat_nome].id,
            )
            sessao.add(t)
            transacoes_criadas += 1

        # Despesas variáveis (8 a 15 por mês)
        for _ in range(random.randint(8, 15)):
            cat_nome = random.choice(list(DESCRICOES_DESPESA.keys()))
            desc = random.choice(DESCRICOES_DESPESA[cat_nome])
            valor = round(random.uniform(15, 600), 2)
            dia = random.randint(1, 28)
            t = Transacao(
                descricao=desc,
                valor=Decimal(str(valor)),
                tipo="despesa",
                data=date(ano, mes, dia),
                conta_id=conta_principal.id,
                categoria_id=cats[cat_nome].id,
            )
            sessao.add(t)
            transacoes_criadas += 1

        # Freelance esporádico (50% de chance)
        if random.random() > 0.5:
            valor_free = round(random.uniform(500, 3000), 2)
            t = Transacao(
                descricao=random.choice(DESCRICOES_RECEITA["Freelance"]),
                valor=Decimal(str(valor_free)),
                tipo="receita",
                data=date(ano, mes, random.randint(1, 28)),
                conta_id=conta_principal.id,
                categoria_id=cats["Freelance"].id,
            )
            sessao.add(t)
            transacoes_criadas += 1

        # Transferência para poupança
        if random.random() > 0.3:
            valor_poupanca = round(random.uniform(200, 800), 2)
            t_saida = Transacao(
                descricao="Transferência para poupança",
                valor=Decimal(str(valor_poupanca)),
                tipo="despesa",
                data=date(ano, mes, 6),
                conta_id=conta_principal.id,
            )
            t_entrada = Transacao(
                descricao="Transferência recebida",
                valor=Decimal(str(valor_poupanca)),
                tipo="receita",
                data=date(ano, mes, 6),
                conta_id=conta_poupanca.id,
            )
            sessao.add(t_saida)
            sessao.add(t_entrada)
            transacoes_criadas += 2

    sessao.flush()
    console.print(f"[green]✅ {transacoes_criadas} transações criadas.[/green]")


def main() -> None:
    """Executa o seed completo."""
    console.print("\nIniciando seed do banco de dados...\n")

    criar_schema()

    with obter_sessao() as sessao:
        # Limpa dados existentes
        sessao.query(Meta).delete()
        sessao.query(Transacao).delete()
        sessao.query(Conta).delete()
        sessao.query(Categoria).delete()
        sessao.flush()

        cats = seed_categorias(sessao)
        contas = seed_contas(sessao)
        seed_metas(sessao, cats)
        seed_transacoes(sessao, contas, cats)

    console.print("\nSeed concluido com sucesso!")
    console.print("Execute: financa dashboard\n")


if __name__ == "__main__":
    main()
