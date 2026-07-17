"""Shared pytest fixtures for CivicPulse backend + NLP tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from backend.app import create_app
from backend.db import SessionLocal, configure_engine

FIXTURES_SIGNALS = Path(__file__).resolve().parent / "fixtures" / "signals"


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret-key")
    db_path = tmp_path / "test.db"
    # Absolute path for sqlite URL on Windows.
    db_url = f"sqlite:///{db_path.as_posix()}"
    configure_engine(db_url)
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
            "SQLALCHEMY_DATABASE_URI": db_url,
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(autouse=True)
def _reset_job_slot():
    import backend.jobs as jobs

    with jobs._job_lock:
        jobs._running_job_id = None
    yield
    with jobs._job_lock:
        jobs._running_job_id = None


@pytest.fixture()
def auth_client(client):
    """Signed-up + logged-in test client (session cookie)."""
    res = client.post(
        "/api/auth/signup",
        json={
            "name": "Test User",
            "email": "tester@example.com",
            "password": "secret12",
        },
    )
    assert res.status_code == 201, res.get_json()
    return client


@pytest.fixture()
def signals_dir() -> Path:
    return FIXTURES_SIGNALS


@pytest.fixture()
def imported_signals(app, signals_dir):
    """Load fixture JSON into the test DB; return total row count."""
    from backend.models import Signal
    from backend.signals_import import import_signals_from_dir

    db = SessionLocal()
    try:
        db.query(Signal).delete()
        db.commit()
    finally:
        db.close()

    totals = import_signals_from_dir(signals_dir)
    return totals["inserted"]
