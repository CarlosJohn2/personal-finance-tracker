"""Serviço de exportação de dados para CSV e PDF."""
from __future__ import annotations

import csv
from decimal import Decimal
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy.orm import Session

from src.config import Config
from src.repositories.transacao_repo import TransacaoRepository

MESES_PT = [
    "",
    "Janeiro", "Fevereiro", "Março", "Abril",
    "Maio", "Junho", "Julho", "Agosto",
    "Setembro", "Outubro", "Novembro", "Dezembro",
]

COR_PRIMARIA = colors.HexColor("#1a1a2e")
COR_SECUNDARIA = colors.HexColor("#16213e")
COR_VERDE = colors.HexColor("#00aa44")
COR_LINHA_PAR = colors.HexColor("#f5f5f5")
COR_BORDA = colors.HexColor("#cccccc")


class ExportacaoService:
    """Exporta dados financeiros para CSV e PDF.

    Args:
        sessao: Sessão ativa do banco de dados.
    """

    def __init__(self, sessao: Session) -> None:
        self.repo = TransacaoRepository(sessao)
        Config.garantir_diretorios()

    def exportar_csv(self, mes: int, ano: int) -> Path:
        """Exporta transações do mês para arquivo CSV.

        Usa ponto-e-vírgula como separador e codificação UTF-8 com BOM
        para compatibilidade com Microsoft Excel.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            Path: Caminho absoluto do arquivo CSV gerado.
        """
        transacoes = self.repo.listar_por_mes_ano(mes, ano)
        caminho = Config.EXPORT_DIR / f"transacoes_{ano}_{mes:02d}.csv"

        with open(caminho, "w", newline="", encoding="utf-8-sig") as arquivo:
            writer = csv.writer(arquivo, delimiter=";")
            writer.writerow([
                "ID", "Data", "Descrição", "Tipo",
                "Valor (R$)", "Conta", "Categoria", "Observação",
            ])
            for t in transacoes:
                writer.writerow([
                    t.id,
                    t.data.strftime("%d/%m/%Y"),
                    t.descricao,
                    t.tipo.capitalize(),
                    f"{t.valor:.2f}".replace(".", ","),
                    t.conta.nome if t.conta else "—",
                    f"{t.categoria.icone} {t.categoria.nome}" if t.categoria else "—",
                    t.observacao or "",
                ])

        return caminho

    def exportar_pdf(self, mes: int, ano: int) -> Path:
        """Exporta relatório do mês para arquivo PDF.

        Inclui resumo financeiro e extrato completo de transações
        com formatação profissional via ReportLab.

        Args:
            mes: Mês (1–12).
            ano: Ano.

        Returns:
            Path: Caminho absoluto do arquivo PDF gerado.
        """
        transacoes = self.repo.listar_por_mes_ano(mes, ano)
        totais = self.repo.totais_por_tipo_mes(mes, ano)

        caminho = Config.EXPORT_DIR / f"relatorio_{ano}_{mes:02d}.pdf"
        doc = SimpleDocTemplate(
            str(caminho),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        estilos = getSampleStyleSheet()

        estilo_titulo = ParagraphStyle(
            "Titulo",
            parent=estilos["Heading1"],
            fontSize=20,
            textColor=COR_PRIMARIA,
            alignment=TA_CENTER,
            spaceAfter=4,
        )
        estilo_subtitulo = ParagraphStyle(
            "Subtitulo",
            parent=estilos["Normal"],
            fontSize=11,
            textColor=colors.HexColor("#666666"),
            alignment=TA_CENTER,
            spaceAfter=16,
        )
        estilo_secao = ParagraphStyle(
            "Secao",
            parent=estilos["Heading2"],
            fontSize=13,
            textColor=COR_PRIMARIA,
            spaceBefore=12,
            spaceAfter=6,
        )

        elementos = []

        # ── Cabeçalho ──────────────────────────────────────────────────
        elementos.append(Paragraph("💰 Personal Finance Tracker", estilo_titulo))
        elementos.append(
            Paragraph(f"Relatório de {MESES_PT[mes]}/{ano}", estilo_subtitulo)
        )
        elementos.append(
            HRFlowable(width="100%", thickness=1.5, color=COR_PRIMARIA, spaceAfter=12)
        )

        # ── Resumo ─────────────────────────────────────────────────────
        receita = totais.get("receita", Decimal("0"))
        despesa = totais.get("despesa", Decimal("0"))
        saldo = receita - despesa

        cor_saldo = COR_VERDE if saldo >= 0 else colors.red

        dados_resumo = [
            ["Indicador", "Valor"],
            ["Total de Receitas", f"R$ {receita:,.2f}"],
            ["Total de Despesas", f"R$ {despesa:,.2f}"],
            ["Saldo do Mês", f"R$ {saldo:,.2f}"],
            ["Número de Transações", str(len(transacoes))],
        ]

        tabela_resumo = Table(dados_resumo, colWidths=[9 * cm, 6 * cm])
        tabela_resumo.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_PRIMARIA),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_LINHA_PAR]),
                ("GRID", (0, 0), (-1, -1), 0.5, COR_BORDA),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("TEXTCOLOR", (1, 3), (1, 3), cor_saldo),
                ("FONTNAME", (1, 3), (1, 3), "Helvetica-Bold"),
            ])
        )

        elementos.append(Paragraph("📋 Resumo Financeiro", estilo_secao))
        elementos.append(tabela_resumo)
        elementos.append(Spacer(1, 0.6 * cm))

        # ── Extrato ────────────────────────────────────────────────────
        elementos.append(Paragraph("📄 Extrato de Transações", estilo_secao))
        elementos.append(Spacer(1, 0.2 * cm))

        dados_trans = [["Data", "Descrição", "Categoria", "Tipo", "Valor"]]
        for t in transacoes:
            cat_str = (
                f"{t.categoria.icone} {t.categoria.nome}" if t.categoria else "—"
            )
            sinal = "+" if t.tipo == "receita" else "-"
            dados_trans.append([
                t.data.strftime("%d/%m/%Y"),
                t.descricao[:38],
                cat_str[:22],
                t.tipo.capitalize(),
                f"{sinal} R$ {t.valor:,.2f}",
            ])

        tabela_trans = Table(
            dados_trans,
            colWidths=[2.5 * cm, 6.5 * cm, 3.5 * cm, 2.5 * cm, 3 * cm],
        )
        tabela_trans.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), COR_SECUNDARIA),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (4, 0), (4, -1), "RIGHT"),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_LINHA_PAR]),
                ("GRID", (0, 0), (-1, -1), 0.25, COR_BORDA),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ])
        )

        elementos.append(tabela_trans)

        doc.build(elementos)
        return caminho
