"""Serviço de geração de relatórios e gráficos."""
from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sqlalchemy.orm import Session

from src.config import Config
from src.repositories.transacao_repo import TransacaoRepository

MESES_PT = [
    "",
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro",
]

ABREVIACOES_PT = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                   "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

COR_FUNDO = "#1e1e2e"
COR_PAINEL = "#313244"
COR_BORDA = "#45475a"
COR_TEXTO = "#cdd6f4"
COR_RECEITA = "#a6e3a1"
COR_DESPESA = "#f38ba8"


class RelatorioService:
    """Gera relatórios financeiros e gráficos matplotlib.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        self.repo = TransacaoRepository(sessao)
        Config.garantir_diretorios()

    def resumo_mensal(self, mes: int, ano: int) -> Dict:
        """Compila o resumo financeiro de um mês.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            dict: Resumo com receitas, despesas, saldo, categorias e total de transações.
        """
        totais = self.repo.totais_por_tipo_mes(mes, ano)
        categorias_raw = self.repo.gastos_por_categoria(mes, ano)
        transacoes = self.repo.listar_por_mes_ano(mes, ano)

        receita = totais.get("receita", Decimal("0"))
        despesa = totais.get("despesa", Decimal("0"))

        return {
            "mes": mes,
            "ano": ano,
            "nome_mes": MESES_PT[mes],
            "receita": receita,
            "despesa": despesa,
            "saldo": receita - despesa,
            "categorias": [
                (nome, icone, cor, Decimal(str(total)))
                for nome, icone, cor, total in categorias_raw
            ],
            "total_transacoes": len(transacoes),
        }

    def historico_anual(self, ano: int) -> Dict:
        """Compila o histórico financeiro de um ano inteiro.

        Args:
            ano: Ano.

        Returns:
            dict: Dados mensais, totais anuais e saldo anual.
        """
        dados_brutos = self.repo.historico_mensal_ano(ano)
        historico: Dict[int, Dict[str, Decimal]] = {
            m: {"receita": Decimal("0"), "despesa": Decimal("0")}
            for m in range(1, 13)
        }

        for mes, tipo, total in dados_brutos:
            historico[int(mes)][tipo] = Decimal(str(total))

        total_receita = sum(v["receita"] for v in historico.values())
        total_despesa = sum(v["despesa"] for v in historico.values())

        return {
            "ano": ano,
            "meses": historico,
            "total_receita": total_receita,
            "total_despesa": total_despesa,
            "saldo_anual": total_receita - total_despesa,
        }

    def gerar_grafico_pizza(self, mes: int, ano: int) -> Path:
        """Gera gráfico de pizza com gastos por categoria.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            Path: Caminho do arquivo PNG gerado.

        Raises:
            ValueError: Se não houver dados de despesa no período.
        """
        categorias = self.repo.gastos_por_categoria(mes, ano)
        if not categorias:
            raise ValueError(f"Sem despesas em {MESES_PT[mes]}/{ano} para gerar gráfico.")

        nomes = [f"{icone} {nome}" for nome, icone, _, _ in categorias]
        valores = [float(total) for _, _, _, total in categorias]
        cores_hex = [cor for _, _, cor, _ in categorias]

        fig, ax = plt.subplots(figsize=(11, 7), facecolor=COR_FUNDO)
        ax.set_facecolor(COR_FUNDO)

        wedges, _, autotexts = ax.pie(
            valores,
            labels=None,
            autopct="%1.1f%%",
            colors=cores_hex,
            startangle=90,
            pctdistance=0.82,
            wedgeprops={"linewidth": 2, "edgecolor": COR_FUNDO},
        )

        for autotext in autotexts:
            autotext.set_color(COR_TEXTO)
            autotext.set_fontsize(9)
            autotext.set_fontweight("bold")

        legend = ax.legend(
            wedges,
            [f"{n}  R$ {v:,.2f}" for n, v in zip(nomes, valores)],
            title="📊 Categorias",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            facecolor=COR_PAINEL,
            edgecolor=COR_BORDA,
            labelcolor=COR_TEXTO,
            title_fontsize=10,
            fontsize=9,
        )
        legend.get_title().set_color(COR_TEXTO)

        ax.set_title(
            f"💸 Gastos por Categoria — {MESES_PT[mes]}/{ano}",
            color=COR_TEXTO,
            fontsize=14,
            fontweight="bold",
            pad=20,
        )

        caminho = Config.CHARTS_DIR / f"pizza_{ano}_{mes:02d}.png"
        plt.tight_layout()
        plt.savefig(str(caminho), dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
        plt.close()
        return caminho

    def gerar_grafico_anual(self, ano: int) -> Path:
        """Gera gráfico de barras com histórico anual comparado.

        Args:
            ano: Ano.

        Returns:
            Path: Caminho do arquivo PNG gerado.
        """
        historico = self.historico_anual(ano)
        meses = list(range(1, 13))
        receitas = [float(historico["meses"][m]["receita"]) for m in meses]
        despesas = [float(historico["meses"][m]["despesa"]) for m in meses]
        saldos = [r - d for r, d in zip(receitas, despesas)]

        x = np.arange(12)
        largura = 0.3

        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=(14, 10), facecolor=COR_FUNDO,
            gridspec_kw={"height_ratios": [3, 1]},
        )

        for ax in (ax1, ax2):
            ax.set_facecolor(COR_FUNDO)
            for spine in ax.spines.values():
                spine.set_color(COR_BORDA)

        # Barras de receita e despesa
        barras_r = ax1.bar(x - largura / 2, receitas, largura,
                           label="Receitas", color=COR_RECEITA, alpha=0.9)
        barras_d = ax1.bar(x + largura / 2, despesas, largura,
                           label="Despesas", color=COR_DESPESA, alpha=0.9)

        ax1.set_title(
            f"📅 Histórico Financeiro — {ano}",
            color=COR_TEXTO, fontsize=14, fontweight="bold", pad=15,
        )
        ax1.set_xticks(x)
        ax1.set_xticklabels(ABREVIACOES_PT, color=COR_TEXTO, fontsize=9)
        ax1.tick_params(colors=COR_TEXTO)
        ax1.set_ylabel("Valor (R$)", color=COR_TEXTO)
        ax1.legend(facecolor=COR_PAINEL, edgecolor=COR_BORDA, labelcolor=COR_TEXTO)
        ax1.yaxis.label.set_color(COR_TEXTO)

        # Linha de saldo líquido
        cores_saldo = [COR_RECEITA if s >= 0 else COR_DESPESA for s in saldos]
        ax2.bar(x, saldos, color=cores_saldo, alpha=0.85)
        ax2.axhline(0, color=COR_BORDA, linewidth=1)
        ax2.set_xticks(x)
        ax2.set_xticklabels(ABREVIACOES_PT, color=COR_TEXTO, fontsize=8)
        ax2.tick_params(colors=COR_TEXTO)
        ax2.set_ylabel("Saldo (R$)", color=COR_TEXTO, fontsize=8)
        ax2.yaxis.label.set_color(COR_TEXTO)
        ax2.set_title("Saldo Líquido Mensal", color=COR_TEXTO, fontsize=10)

        caminho = Config.CHARTS_DIR / f"anual_{ano}.png"
        plt.tight_layout(pad=2.0)
        plt.savefig(str(caminho), dpi=150, bbox_inches="tight", facecolor=COR_FUNDO)
        plt.close()
        return caminho
