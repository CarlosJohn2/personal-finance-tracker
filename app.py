"""Servidor web Flask — Personal Finance Tracker."""
from __future__ import annotations

import threading
import webbrowser
from datetime import date
from decimal import Decimal

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for

from src.database.conexao import obter_sessao
from src.models.transacao import TipoTransacao
from src.repositories.categoria_repo import CategoriaRepository
from src.repositories.conta_repo import ContaRepository
from src.services.exportacao_service import ExportacaoService
from src.services.meta_service import MetaService
from src.services.relatorio_service import MESES_PT, RelatorioService
from src.services.transacao_service import TransacaoService

app = Flask(__name__)
app.secret_key = "finance-tracker-secret-2024"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _decimal(v) -> float:
    return float(v) if v else 0.0


# ── Rotas principais ──────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    hoje = date.today()
    mes = int(request.args.get("mes", hoje.month))
    ano = int(request.args.get("ano", hoje.year))

    with obter_sessao() as sessao:
        trans_svc = TransacaoService(sessao)
        rel_svc = RelatorioService(sessao)
        meta_svc = MetaService(sessao)
        conta_repo = ContaRepository(sessao)

        resumo = rel_svc.resumo_mensal(mes, ano)
        historico = rel_svc.historico_anual(ano)
        transacoes = trans_svc.listar(limite=10)
        metas = meta_svc.listar_ativas()
        alertas = meta_svc.verificar_alertas()
        cat_repo = CategoriaRepository(sessao)
        contas = conta_repo.listar_ordenado()
        categorias_db = cat_repo.listar_ordenado()
        saldos = {c.id: _decimal(trans_svc.saldo_conta(c.id)) for c in contas}
        saldo_total = _decimal(trans_svc.saldo_total())

        # Dados para gráfico de barras anual
        labels_anual = [m[:3] for m in MESES_PT[1:]]
        receitas_anual = [_decimal(historico["meses"][m]["receita"]) for m in range(1, 13)]
        despesas_anual = [_decimal(historico["meses"][m]["despesa"]) for m in range(1, 13)]

        # Dados para gráfico de pizza de categorias
        cats_pizza = [
            {"nome": f"{icone} {nome}", "valor": _decimal(total)}
            for nome, icone, _, total in resumo["categorias"]
        ]

        contas_data = [
            {
                "id": c.id,
                "nome": c.nome,
                "tipo": c.tipo,
                "icone": c.icone,
                "saldo_inicial": _decimal(c.saldo_inicial),
                "saldo_atual": saldos[c.id],
            }
            for c in contas
        ]

        categorias_data = [
            {"id": c.id, "nome": c.nome, "icone": c.icone, "tipo": c.tipo}
            for c in categorias_db
        ]

        trans_data = [
            {
                "id": t.id,
                "data": t.data.strftime("%d/%m/%Y"),
                "descricao": t.descricao,
                "tipo": t.tipo,
                "valor": _decimal(t.valor),
                "categoria": f"{t.categoria.icone} {t.categoria.nome}" if t.categoria else "—",
                "conta": t.conta.nome if t.conta else "—",
            }
            for t in transacoes
        ]

        metas_data = [
            {
                "id": m.id,
                "nome": m.nome,
                "valor_alvo": _decimal(m.valor_alvo),
                "valor_atual": _decimal(m.valor_atual),
                "restante": _decimal(m.restante),
                "percentual": round(m.percentual, 1),
                "concluida": m.concluida,
                "prazo": m.data_limite.strftime("%d/%m/%Y") if m.data_limite else None,
            }
            for m in metas
        ]

    return render_template(
        "dashboard.html",
        saldo_total=saldo_total,
        resumo=resumo,
        contas=contas_data,
        categorias=categorias_data,
        transacoes=trans_data,
        metas=metas_data,
        alertas=alertas,
        cats_pizza=cats_pizza,
        labels_anual=labels_anual,
        receitas_anual=receitas_anual,
        despesas_anual=despesas_anual,
        mes=mes,
        ano=ano,
        meses_pt=MESES_PT,
        hoje=date.today(),
    )


@app.route("/transacoes")
def transacoes():
    mes = int(request.args.get("mes", date.today().month))
    ano = int(request.args.get("ano", date.today().year))

    with obter_sessao() as sessao:
        svc = TransacaoService(sessao)
        cat_repo = CategoriaRepository(sessao)
        conta_repo = ContaRepository(sessao)

        lista = svc.listar_por_mes(mes, ano)
        categorias_raw = cat_repo.listar_ordenado()
        contas_raw = conta_repo.listar_ordenado()

        categorias = [{"id": c.id, "nome": c.nome, "icone": c.icone, "tipo": c.tipo} for c in categorias_raw]
        contas = [{"id": c.id, "nome": c.nome, "icone": c.icone} for c in contas_raw]

        trans_data = [
            {
                "id": t.id,
                "data": t.data.strftime("%d/%m/%Y"),
                "descricao": t.descricao,
                "tipo": t.tipo,
                "valor": _decimal(t.valor),
                "categoria": f"{t.categoria.icone} {t.categoria.nome}" if t.categoria else "—",
                "conta": t.conta.nome if t.conta else "—",
                "observacao": t.observacao or "",
            }
            for t in lista
        ]

    return render_template(
        "transacoes.html",
        transacoes=trans_data,
        categorias=categorias,
        contas=contas,
        mes=mes,
        ano=ano,
        meses_pt=MESES_PT,
        hoje=date.today(),
    )


@app.route("/transacoes/nova", methods=["POST"])
def nova_transacao():
    from datetime import datetime
    data = request.form
    try:
        with obter_sessao() as sessao:
            svc = TransacaoService(sessao)
            svc.adicionar(
                descricao=data["descricao"],
                valor=Decimal(data["valor"].replace(",", ".")),
                tipo=data["tipo"],
                data=datetime.strptime(data["data"], "%Y-%m-%d").date(),
                conta_id=int(data["conta_id"]),
                categoria_id=int(data["categoria_id"]) if data.get("categoria_id") else None,
                observacao=data.get("observacao") or None,
            )
        flash("Transação registrada com sucesso!", "success")
    except Exception as e:
        flash(f"Erro ao registrar transação: {e}", "error")
    return redirect(url_for("transacoes", mes=data.get("mes", date.today().month), ano=data.get("ano", date.today().year)))


@app.route("/transacoes/<int:id>/deletar", methods=["POST"])
def deletar_transacao(id: int):
    with obter_sessao() as sessao:
        TransacaoService(sessao).remover(id)
    flash("Transação removida.", "success")
    return redirect(url_for("transacoes"))


@app.route("/metas")
def metas():
    with obter_sessao() as sessao:
        svc = MetaService(sessao)
        todas = svc.listar_todas()
        alertas = svc.verificar_alertas()
        metas_data = [
            {
                "id": m.id,
                "nome": m.nome,
                "valor_alvo": _decimal(m.valor_alvo),
                "valor_atual": _decimal(m.valor_atual),
                "restante": _decimal(m.restante),
                "percentual": round(m.percentual, 1),
                "concluida": m.concluida,
                "ativa": m.ativa,
                "prazo": m.data_limite.strftime("%d/%m/%Y") if m.data_limite else None,
            }
            for m in todas
        ]
    return render_template("metas.html", metas=metas_data, alertas=alertas, hoje=date.today())


@app.route("/metas/nova", methods=["POST"])
def nova_meta():
    from datetime import datetime
    data = request.form
    prazo = None
    if data.get("data_limite"):
        prazo = datetime.strptime(data["data_limite"], "%Y-%m-%d").date()
    with obter_sessao() as sessao:
        MetaService(sessao).criar(
            nome=data["nome"],
            valor_alvo=Decimal(data["valor_alvo"].replace(",", ".")),
            data_limite=prazo,
        )
    flash(f"Meta '{data['nome']}' criada com sucesso!", "success")
    return redirect(url_for("metas"))


@app.route("/metas/<int:id>/depositar", methods=["POST"])
def depositar_meta(id: int):
    valor = Decimal(request.form["valor"].replace(",", "."))
    with obter_sessao() as sessao:
        MetaService(sessao).depositar(id, valor)
    flash(f"Aporte de R$ {float(valor):.2f} registrado!", "success")
    return redirect(url_for("metas"))


@app.route("/metas/<int:id>/encerrar", methods=["POST"])
def encerrar_meta(id: int):
    with obter_sessao() as sessao:
        MetaService(sessao).encerrar(id)
    flash("Meta encerrada.", "success")
    return redirect(url_for("metas"))


@app.route("/relatorios")
def relatorios():
    mes = int(request.args.get("mes", date.today().month))
    ano = int(request.args.get("ano", date.today().year))

    with obter_sessao() as sessao:
        rel_svc = RelatorioService(sessao)
        resumo = rel_svc.resumo_mensal(mes, ano)
        historico = rel_svc.historico_anual(ano)

        labels_anual = [m[:3] for m in MESES_PT[1:]]
        receitas_anual = [_decimal(historico["meses"][m]["receita"]) for m in range(1, 13)]
        despesas_anual = [_decimal(historico["meses"][m]["despesa"]) for m in range(1, 13)]
        cats_pizza = [
            {"nome": f"{icone} {nome}", "valor": _decimal(total)}
            for nome, icone, _, total in resumo["categorias"]
        ]

    return render_template(
        "relatorios.html",
        resumo=resumo,
        historico=historico,
        cats_pizza=cats_pizza,
        labels_anual=labels_anual,
        receitas_anual=receitas_anual,
        despesas_anual=despesas_anual,
        mes=mes,
        ano=ano,
        meses_pt=MESES_PT,
        hoje=date.today(),
    )


@app.route("/relatorios/exportar")
def exportar():
    mes = int(request.args.get("mes", date.today().month))
    ano = int(request.args.get("ano", date.today().year))
    fmt = request.args.get("formato", "csv")
    with obter_sessao() as sessao:
        svc = ExportacaoService(sessao)
        if fmt == "pdf":
            caminho = svc.exportar_pdf(mes, ano)
        else:
            caminho = svc.exportar_csv(mes, ano)
    return jsonify({"arquivo": str(caminho), "ok": True})


if __name__ == "__main__":
    def abrir_browser():
        import time
        time.sleep(1)
        webbrowser.open("http://127.0.0.1:5000")

    threading.Thread(target=abrir_browser, daemon=True).start()
    app.run(debug=False, port=5000)
