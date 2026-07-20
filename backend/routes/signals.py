"""Signals + config API (DB-backed with JSON fallback)."""

from __future__ import annotations

import json
import sys

from flask import Blueprint, jsonify

from backend.config import NEWS_DEFAULTS, ROOT, SIGNALS_DIR, TIKTOK_DEFAULTS
from backend.db import get_session
from backend.models import Signal

bp = Blueprint("signals", __name__)


def _read_json(path, default):
    if not path.is_file():
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _signals_from_db() -> list[dict]:
    db = get_session()
    rows = db.query(Signal).order_by(Signal.id.asc()).all()
    return [row.to_dict() for row in rows]


def _signals_from_json() -> list[dict]:
    tiktok = _read_json(SIGNALS_DIR / "tiktok.json", [])
    reddit = _read_json(SIGNALS_DIR / "reddit.json", [])
    twitter = _read_json(SIGNALS_DIR / "twitter.json", [])
    news = _read_json(SIGNALS_DIR / "news.json", [])
    return tiktok + reddit + twitter + news


@bp.get("/api/signals")
def api_signals():
    """Prefer SQLite after import; JSON files are fallback only when the table is empty."""
    signals = _signals_from_db()
    if signals:
        return jsonify({"count": len(signals), "signals": signals, "storage": "db"})
    signals = _signals_from_json()
    return jsonify({"count": len(signals), "signals": signals, "storage": "json"})


@bp.get("/api/signals/feed")
def api_feed():
    """Landing feed from SQLite when present; else data/signals/feed.json."""
    db = get_session()
    rows = db.query(Signal).order_by(Signal.id.asc()).all()
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
