"""Path B durability: stable_id, ponds, backup gates, no default prune."""

from __future__ import annotations

import json
from pathlib import Path

from backend.db import SessionLocal
from backend.db_backup import backup_database, require_backup
from backend.models import Signal
from backend.pool import bootstrap_ponds, merge_into_pond, read_pond
from backend.signals_import import (
    archive_missing_signals,
    import_signals_from_dir,
    prune_orphan_signals,
)
from backend.stable_id import compute_stable_id, ensure_stable_id


def _write_json(path: Path, rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2), encoding="utf-8")


def test_stable_id_url_stable_across_title_change():
    a = compute_stable_id("reddit", "https://reddit.com/r/x/comments/1", "Old", "same body")
    b = compute_stable_id("reddit", "https://reddit.com/r/x/comments/1", "New title", "same body")
    assert a == b
    assert len(a) == 40


def test_stable_id_disambiguates_shared_url():
    a = compute_stable_id("tiktok", "https://tiktok.com/@u/video/1", "c1", "comment one")
    b = compute_stable_id("tiktok", "https://tiktok.com/@u/video/1", "c2", "comment two")
    assert a != b


def test_pond_merge_idempotent(tmp_path):
    pool = tmp_path / "pool"
    rows = [
        {
            "source": "reddit",
            "title": "A",
            "body": "b",
            "url": "https://example.com/a",
            "categories": [],
            "published_utc": "2026-01-01",
            "outlet": "r/x",
            "metadata": {},
        }
    ]
    first = merge_into_pond("reddit", rows, pool)
    assert first["inserted"] == 1
    rows[0]["title"] = "A updated"
    second = merge_into_pond("reddit", rows, pool)
    assert second["inserted"] == 0
    assert second["updated"] == 1
    assert second["total"] == 1
    assert read_pond("reddit", pool)[0]["title"] == "A updated"


def test_import_idempotent_on_stable_id(app, signals_dir):
    first = import_signals_from_dir(signals_dir)
    assert first["inserted"] == 10
    second = import_signals_from_dir(signals_dir)
    assert second["inserted"] == 0
    assert second["updated"] == 10


def test_smaller_export_does_not_delete_without_flags(app, tmp_path, signals_dir):
    import_signals_from_dir(signals_dir)
    db = SessionLocal()
    try:
        before = db.query(Signal).count()
    finally:
        db.close()

    small = tmp_path / "signals"
    # Keep only reddit fixture rows (2) — other sources' files missing would break
    # archive; for upsert-only we pass only reddit.
    _write_json(small / "reddit.json", json.loads((signals_dir / "reddit.json").read_text()))
    totals = import_signals_from_dir(small, sources=("reddit",))
    assert totals["updated"] + totals["inserted"] >= 1

    db = SessionLocal()
    try:
        after = db.query(Signal).count()
        assert after == before
    finally:
        db.close()


def test_archive_missing_scoped_to_source(app, tmp_path, signals_dir):
    import_signals_from_dir(signals_dir)
    small = tmp_path / "signals"
    # One reddit row only
    reddit = json.loads((signals_dir / "reddit.json").read_text())[:1]
    _write_json(small / "reddit.json", reddit)

    archived = archive_missing_signals(small, sources=("reddit",))
    assert archived == 1

    db = SessionLocal()
    try:
        active_reddit = (
            db.query(Signal)
            .filter(Signal.source == "reddit", Signal.archived_at.is_(None))
            .count()
        )
        tiktok = (
            db.query(Signal)
            .filter(Signal.source == "tiktok", Signal.archived_at.is_(None))
            .count()
        )
        assert active_reddit == 1
        assert tiktok == 4
    finally:
        db.close()


def test_prune_scoped_and_requires_non_empty(app, tmp_path, signals_dir):
    import_signals_from_dir(signals_dir)
    empty = tmp_path / "signals"
    _write_json(empty / "reddit.json", [])
    try:
        prune_orphan_signals(empty, sources=("reddit",), allow_empty=False)
        assert False, "expected RuntimeError"
    except RuntimeError:
        pass

    one = json.loads((signals_dir / "reddit.json").read_text())[:1]
    _write_json(empty / "reddit.json", one)
    pruned = prune_orphan_signals(empty, sources=("reddit",))
    assert pruned == 1

    db = SessionLocal()
    try:
        assert db.query(Signal).filter(Signal.source == "reddit").count() == 1
        assert db.query(Signal).filter(Signal.source == "tiktok").count() == 4
    finally:
        db.close()


def test_backup_before_destructive(app, tmp_path, monkeypatch):
    # Point DATABASE_URL already set by app fixture; create a real sqlite file.
    from backend.db import get_engine

    eng = get_engine()
    db_path = Path(str(eng.url).replace("sqlite:///", ""))
    assert db_path.is_file()
    backup_dir = tmp_path / "backups"
    path = backup_database(db_path=db_path, backup_dir=backup_dir)
    assert path is not None
    assert path.is_file()
    assert "civicpulse_" in path.name

    required = require_backup(db_path=db_path, backup_dir=backup_dir)
    assert required.is_file()


def test_api_lists_after_import(client, imported_signals):
    res = client.get("/api/signals")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["storage"] == "sqlite"
    assert payload["count"] == imported_signals


def test_api_hides_archived(client, app, signals_dir):
    import_signals_from_dir(signals_dir)
    db = SessionLocal()
    try:
        row = db.query(Signal).filter(Signal.source == "reddit").first()
        from backend.models import utcnow

        row.archived_at = utcnow()
        db.commit()
    finally:
        db.close()

    res = client.get("/api/signals")
    payload = res.get_json()
    assert payload["count"] == 9


def test_bootstrap_and_reprocess_resurrects(tmp_path, signals_dir):
    pool = tmp_path / "pool"
    # Pond has civic + a reject that later gets categories via ensure + manual
    civic = json.loads((signals_dir / "reddit.json").read_text())
    reject = {
        "source": "reddit",
        "outlet": "r/irvine",
        "title": "Housing costs keep climbing in Irvine",
        "body": "Rent and housing prices are out of control for residents",
        "url": "https://reddit.com/r/irvine/comments/housing1",
        "categories": [],
        "published_utc": "2026-07-05",
        "metadata": {},
    }
    ensure_stable_id(reject)
    bootstrap_ponds(pool_dir=pool, signals_dir=signals_dir, sources=("reddit",))
    merge_into_pond("reddit", [reject], pool)
    pond = read_pond("reddit", pool)
    assert len(pond) >= 3

    # Derive signals = rows with categories (simulate reprocess output)
    # Give reject categories as if classifier improved
    for row in pond:
        if row["url"] == reject["url"]:
            row["categories"] = ["housing"]
    merge_into_pond("reddit", pond, pool)
    signals = [r for r in read_pond("reddit", pool) if r.get("categories")]
    assert any(r["url"] == reject["url"] for r in signals)
