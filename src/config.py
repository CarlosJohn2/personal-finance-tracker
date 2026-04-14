"""Configurações gerais da aplicação."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent


class Config:
    """Configurações carregadas a partir de variáveis de ambiente.

    Attributes:
        DATABASE_URL: URL de conexão com o banco MySQL.
        ECHO_SQL: Se True, exibe queries SQL no terminal.
        EXPORT_DIR: Diretório para arquivos exportados (CSV/PDF).
        CHARTS_DIR: Diretório para gráficos gerados.
    """

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'finance.db'}",
    )
    ECHO_SQL: bool = os.getenv("ECHO_SQL", "false").lower() == "true"
    EXPORT_DIR: Path = BASE_DIR / "exports"
    CHARTS_DIR: Path = BASE_DIR / "charts"

    @classmethod
    def garantir_diretorios(cls) -> None:
        """Cria os diretórios de saída se não existirem."""
        cls.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
        cls.CHARTS_DIR.mkdir(parents=True, exist_ok=True)
