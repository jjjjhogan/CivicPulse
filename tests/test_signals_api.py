"""Signals API after DB import — SQLite preferred over JSON."""

from __future__ import annotations

from backend.db import SessionLocal
from backend.models import Signal


def test_signals_from_db(client, imported_signals):
    res = client.get("/api/signals")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == imported_signals
    assert len(data["signals"]) == imported_signals
    assert data["storage"] == "db"
    for row in data["signals"]:
        assert "source" in row
        assert "title" in row
        assert isinstance(row.get("categories"), list)


def test_signals_feed_from_db(client, imported_signals):
    res = client.get("/api/signals/feed")
    assert res.status_code == 200
    data = res.get_json()
    assert data["storage"] == "db"
    assert data["count"] == imported_signals
    assert len(data["signals"]) == imported_signals


def test_signals_prefer_db_over_stale_json(client, tmp_path, monkeypatch, imported_signals):
    """When SQLite has rows, API must not silently serve JSON instead."""
    fake_dir = tmp_path / "signals"
    fake_dir.mkdir()
    (fake_dir / "tiktok.json").write_text(
        '[{"source":"tiktok","title":"STALE JSON ONLY","url":"http://stale.example","categories":[],"outlet":"x","published_utc":"2099-01-01","metadata":{}}]',
        encoding="utf-8",
    )
    for name in ("reddit.json", "twitter.json", "news.json", "feed.json"):
        (fake_dir / name).write_text("[]", encoding="utf-8")

    monkeypatch.setattr("backend.routes.signals.SIGNALS_DIR", fake_dir)

    res = client.get("/api/signals")
    data = res.get_json()
    assert data["storage"] == "db"
    titles = {row["title"] for row in data["signals"]}
    assert "STALE JSON ONLY" not in titles
    assert data["count"] == imported_signals


def test_signals_json_fallback_when_db_empty(client, monkeypatch, tmp_path):
    db = SessionLocal()
    try:
        db.query(Signal).delete()
        db.commit()
    finally:
        db.close()

    fake_dir = tmp_path / "signals"
    fake_dir.mkdir()
    (fake_dir / "news.json").write_text(
        '[{"source":"news","title":"From JSON","url":"http://json.example","categories":["housing"],"outlet":"Voice","published_utc":"2026-01-01","metadata":{}}]',
        encoding="utf-8",
    )
    for name in ("tiktok.json", "reddit.json", "twitter.json"):
        (fake_dir / name).write_text("[]", encoding="utf-8")
    (fake_dir / "feed.json").write_text("[]", encoding="utf-8")

    monkeypatch.setattr("backend.routes.signals.SIGNALS_DIR", fake_dir)

    res = client.get("/api/signals")
    data = res.get_json()
    assert data["storage"] == "json"
    assert data["count"] == 1
    assert data["signals"][0]["title"] == "From JSON"


def test_config_endpoint(client):
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.get_json()
    assert "categories" in data
    assert "tiktok_defaults" in data
    assert "news_defaults" in data
    assert "news_outlets" in data
