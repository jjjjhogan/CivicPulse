"""SQLAlchemy engine and request-scoped sessions."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from flask import g
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import DB_PATH, database_url


class Base(DeclarativeBase):
    pass


engine = create_engine(
    database_url(),
    connect_args={"check_same_thread": False},
    future=True,
)

if database_url().startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    from backend import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session() -> Session:
    """Return the SQLAlchemy session for the current Flask request."""
    if "db" not in g:
        g.db = SessionLocal()
    return g.db


def remove_session() -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
