"""SQLAlchemy engine and request-scoped sessions."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from flask import g
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import DB_PATH, database_url


class Base(DeclarativeBase):
    pass


engine: Engine | None = None
SessionLocal = sessionmaker(autoflush=False, autocommit=False, future=True)


def configure_engine(url: str | None = None) -> Engine:
    """Create (or replace) the global engine. Safe to call from tests."""
    global engine

    if engine is not None:
        engine.dispose()

    resolved = url or database_url()
    connect_args = {"check_same_thread": False} if resolved.startswith("sqlite") else {}
    new_engine = create_engine(resolved, connect_args=connect_args, future=True)

    if resolved.startswith("sqlite"):

        @event.listens_for(new_engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record):  # noqa: ANN001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    engine = new_engine
    SessionLocal.configure(bind=engine)
    return engine


def get_engine() -> Engine:
    if engine is None:
        configure_engine()
    assert engine is not None
    return engine


def init_db() -> None:
    eng = get_engine()
    if str(eng.url).startswith("sqlite"):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    from backend import models  # noqa: F401

    Base.metadata.create_all(bind=eng)


def get_session() -> Session:
    """Return the SQLAlchemy session for the current Flask request."""
    if "db" not in g:
        get_engine()
        g.db = SessionLocal()
    return g.db


def remove_session() -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    get_engine()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
