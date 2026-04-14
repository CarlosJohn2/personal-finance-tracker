"""Schema inicial — tabelas principais do sistema.

Revision ID: 001
Revises:
Create Date: 2025-04-13 00:00:00.000000
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria as tabelas: categorias, contas, transacoes, metas."""

    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("icone", sa.String(length=10), nullable=False, server_default="💰"),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("cor", sa.String(length=7), nullable=False, server_default="#00ff88"),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    op.create_table(
        "contas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False, server_default="corrente"),
        sa.Column("saldo_inicial", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0.00"),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )

    op.create_table(
        "transacoes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("descricao", sa.String(length=255), nullable=False),
        sa.Column("valor", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("tipo", sa.String(length=10), nullable=False),
        sa.Column("data", sa.Date(), nullable=False),
        sa.Column("conta_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("observacao", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["conta_id"], ["contas.id"]),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transacoes_data", "transacoes", ["data"])
    op.create_index("ix_transacoes_conta_data", "transacoes", ["conta_id", "data"])
    op.create_index("ix_transacoes_categoria", "transacoes", ["categoria_id"])
    op.create_index("ix_transacoes_tipo_data", "transacoes", ["tipo", "data"])

    op.create_table(
        "metas",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("valor_alvo", sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column("valor_atual", sa.Numeric(precision=15, scale=2), nullable=False, server_default="0.00"),
        sa.Column("data_limite", sa.Date(), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), server_default=sa.text("NOW()"), nullable=False),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Remove todas as tabelas na ordem inversa."""
    op.drop_table("metas")
    op.drop_index("ix_transacoes_tipo_data", table_name="transacoes")
    op.drop_index("ix_transacoes_categoria", table_name="transacoes")
    op.drop_index("ix_transacoes_conta_data", table_name="transacoes")
    op.drop_index("ix_transacoes_data", table_name="transacoes")
    op.drop_table("transacoes")
    op.drop_table("contas")
    op.drop_table("categorias")
