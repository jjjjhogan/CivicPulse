"""Import fixture signals into SQLite."""

from backend.db import SessionLocal
from backend.models import Signal
from backend.signals_import import import_signals_from_dir


def test_import_fixture_signals(app, signals_dir):
    db = SessionLocal()
    try:
        db.query(Signal).delete()
        db.commit()
    finally:
        db.close()

    totals = import_signals_from_dir(signals_dir)
    assert totals["inserted"] == 9  # 3 tiktok + 2 reddit + 2 twitter + 2 news
    assert totals["by_source"]["tiktok"]["inserted"] == 3
    assert totals["by_source"]["reddit"]["inserted"] == 2
    assert totals["by_source"]["twitter"]["inserted"] == 2
    assert totals["by_source"]["news"]["inserted"] == 2

    db = SessionLocal()
    try:
        assert db.query(Signal).count() == 9
    finally:
        db.close()


def test_import_replace_wipes_then_reloads(app, signals_dir):
    import_signals_from_dir(signals_dir)
    db = SessionLocal()
    try:
        deleted = db.query(Signal).delete()
        db.commit()
        assert deleted == 9
    finally:
        db.close()

    totals = import_signals_from_dir(signals_dir)
    assert totals["inserted"] == 9
