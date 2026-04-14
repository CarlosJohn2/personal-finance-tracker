"""Gerenciamento de conexão com o banco de dados via SQLAlchemy."""
from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from src.config import Config

_is_sqlite = Config.DATABASE_URL.startswith("sqlite")
_engine_kwargs: dict = {"echo": Config.ECHO_SQL}
if not _is_sqlite:
    _engine_kwargs.update({"pool_pre_ping": True, "pool_size": 5, "max_overflow": 10})

engine = create_engine(Config.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


@contextmanager
def obter_sessao() -> Generator[Session, None, None]:
    """Context manager que fornece uma sessão transacional segura.

    Realiza commit automático em caso de sucesso e rollback em exceções.

    Yields:
        Session: Sessão ativa do SQLAlchemy.

    Example:
        >>> with obter_sessao() as sessao:
        ...     contas = sessao.query(Conta).all()
    """
    sessao = SessionLocal()
    try:
        yield sessao
        sessao.commit()
    except Exception:
        sessao.rollback()
        raise
    finally:
        sessao.close()


def testar_conexao() -> bool:
    """Verifica se a conexão com o banco está funcionando.

    Returns:
        bool: True se conectou com sucesso.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
