"""Signals + config API (store-backed with JSON fallback)."""

from __future__ import annotations

import json
import sys

from flask import Blueprint, jsonify

from backend.config import DATA_BACKEND, NEWS_DEFAULTS, ROOT, SIGNALS_DIR, TIKTOK_DEFAULTS
from backend.config import NEWS_DEFAULTS, ROOT, SIGNALS_DIR, TIKTOK_DEFAULTS
from backend.db import get_session
from backend.models import Signal
from backend.store import get_signal_store

bp = Blueprint("signals", __name__)


def _read_json(path, default):
    if not path.is_file():
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _signals_from_db() -> list[dict]:
    return get_signal_store().list_signals(include_archived=False)


def _signals_from_json() -> list[dict]:
    tiktok = _read_json(SIGNALS_DIR / "tiktok.json", [])
    reddit = _read_json(SIGNALS_DIR / "reddit.json", [])
    twitter = _read_json(SIGNALS_DIR / "twitter.json", [])
    news = _read_json(SIGNALS_DIR / "news.json", [])
    return tiktok + reddit + twitter + news


@bp.get("/api/signals")
def api_signals():
    """Store-backed signal list; JSON files are fallback only for sqlite with empty table."""
    store = get_signal_store()
    signals = store.list_signals()
    if signals:
        return jsonify({"count": len(signals), "signals": signals, "storage": DATA_BACKEND})
    if DATA_BACKEND == "sqlite":
        signals = _signals_from_json()
        if signals:
            return jsonify({"count": len(signals), "signals": signals, "storage": "json"})
    return jsonify({"count": 0, "signals": [], "storage": DATA_BACKEND})


@bp.get("/api/signals/feed")
def api_feed():
    """Landing feed from store; JSON fallback for sqlite only."""
    store = get_signal_store()
    feed = store.list_feed_signals()
    if feed:
        return jsonify({"count": len(feed), "signals": feed, "storage": DATA_BACKEND})
    if DATA_BACKEND == "sqlite":
        feed = _read_json(SIGNALS_DIR / "feed.json", [])
        if feed:
            return jsonify({"count": len(feed), "signals": feed, "storage": "json"})
    return jsonify({"count": 0, "signals": [], "storage": DATA_BACKEND})
    """Landing feed from SQLite when present; else data/signals/feed.json."""
    db = get_session()
    rows = (
        db.query(Signal)
        .filter(Signal.archived_at.is_(None))
        .order_by(Signal.id.asc())
        .all()
    )
    if rows:
        feed = [row.to_feed_dict() for row in rows]
        return jsonify({"count": len(feed), "signals": feed, "storage": "db"})
    feed = _read_json(SIGNALS_DIR / "feed.json", [])
    return jsonify({"count": len(feed), "signals": feed, "storage": "json"})


@bp.get("/api/manifest")
def api_manifest():
    manifest = _read_json(SIGNALS_DIR / "manifest.json", None)
    return jsonify({"manifest": manifest})


@bp.get("/api/config")
def api_config():
    sys.path.insert(0, str(ROOT))
    from scrapers.categories import CivicIssueCategory  # noqa: WPS433
    from scrapers.news.scrape import NEWS_SOURCES  # noqa: WPS433

    return jsonify(
        {
            "categories": [c.value for c in CivicIssueCategory],
            "tiktok_defaults": TIKTOK_DEFAULTS,
            "news_defaults": NEWS_DEFAULTS,
            "news_outlets": [
                {"id": source["id"], "name": source["name"], "scope": source["scope"]}
                for source in NEWS_SOURCES
            ],
        }
    )
