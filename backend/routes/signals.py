"""Signals + config API (store-backed with JSON fallback)."""

from __future__ import annotations

import json
import sys

from flask import Blueprint, jsonify, request

import backend.config as _cfg
from backend.auth import scrapers_host_ok
from backend.config import NEWS_DEFAULTS, ROOT, SIGNALS_DIR, TIKTOK_DEFAULTS
from backend.store import get_signal_store

bp = Blueprint("signals", __name__)

# Cap dashboard / default list reads so Firestore free tier is not drained.
DEFAULT_SIGNAL_LIMIT = 250
MAX_SIGNAL_LIMIT = 1000


def _read_json(path, default):
    if not path.is_file():
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _signals_from_json() -> list[dict]:
    tiktok = _read_json(SIGNALS_DIR / "tiktok.json", [])
    reddit = _read_json(SIGNALS_DIR / "reddit.json", [])
    twitter = _read_json(SIGNALS_DIR / "twitter.json", [])
    news = _read_json(SIGNALS_DIR / "news.json", [])
    return tiktok + reddit + twitter + news


def _parse_paging():
    raw_limit = request.args.get("limit")
    raw_offset = request.args.get("offset", 0, type=int) or 0
    offset = max(0, raw_offset)
    if raw_limit is None:
        limit = DEFAULT_SIGNAL_LIMIT
    else:
        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = DEFAULT_SIGNAL_LIMIT
        if limit <= 0:
            limit = DEFAULT_SIGNAL_LIMIT
        limit = min(limit, MAX_SIGNAL_LIMIT)
    return limit, offset


@bp.get("/api/signals")
def api_signals():
    """Store-backed signal list; JSON files are fallback only for sqlite with empty table."""
    store = get_signal_store()
    limit, offset = _parse_paging()
    total = store.count_signals()
    signals = store.list_signals(limit=limit, offset=offset)
    if signals or total:
        return jsonify({
            "count": len(signals),
            "total": total,
            "limit": limit,
            "offset": offset,
            "signals": signals,
            "storage": _cfg.DATA_BACKEND,
        })
    if _cfg.DATA_BACKEND == "sqlite":
        signals = _signals_from_json()
        if signals:
            sliced = signals[offset: offset + limit]
            return jsonify({
                "count": len(sliced),
                "total": len(signals),
                "limit": limit,
                "offset": offset,
                "signals": sliced,
                "storage": "json",
            })
    return jsonify({
        "count": 0,
        "total": 0,
        "limit": limit,
        "offset": offset,
        "signals": [],
        "storage": _cfg.DATA_BACKEND,
    })


@bp.get("/api/signals/feed")
def api_feed():
    """Landing feed from store; JSON fallback for sqlite only."""
    store = get_signal_store()
    limit, offset = _parse_paging()
    feed = store.list_feed_signals(limit=limit, offset=offset)
    if feed:
        return jsonify({
            "count": len(feed),
            "limit": limit,
            "offset": offset,
            "signals": feed,
            "storage": _cfg.DATA_BACKEND,
        })
    if _cfg.DATA_BACKEND == "sqlite":
        feed = _read_json(SIGNALS_DIR / "feed.json", [])
        if feed:
            sliced = feed[offset: offset + limit]
            return jsonify({
                "count": len(sliced),
                "limit": limit,
                "offset": offset,
                "signals": sliced,
                "storage": "json",
            })
    return jsonify({
        "count": 0,
        "limit": limit,
        "offset": offset,
        "signals": [],
        "storage": _cfg.DATA_BACKEND,
    })


@bp.get("/api/manifest")
def api_manifest():
    manifest = _read_json(SIGNALS_DIR / "manifest.json", None)
    return jsonify({"manifest": manifest})


@bp.get("/api/config")
def api_config():
    sys.path.insert(0, str(ROOT))
    from scrapers.categories import CivicIssueCategory, DEFAULT_SEARCH_TERMS  # noqa: WPS433
    from scrapers.news.scrape import NEWS_SOURCES  # noqa: WPS433
    from backend.config import TIKTOK_TAG_OPTIONS  # noqa: WPS433
    from backend.jobs import selenium_available  # noqa: WPS433

    return jsonify(
        {
            "categories": [c.value for c in CivicIssueCategory],
            "category_keywords": {
                cat.value: terms
                for cat, terms in DEFAULT_SEARCH_TERMS.items()
            },
            "tiktok_defaults": TIKTOK_DEFAULTS,
            "tiktok_tags": TIKTOK_TAG_OPTIONS,
            "tiktok_available": selenium_available(),
            "news_defaults": NEWS_DEFAULTS,
            "news_outlets": [
                {"id": source["id"], "name": source["name"], "scope": source["scope"]}
                for source in NEWS_SOURCES
            ],
            "scrapers_available": scrapers_host_ok(),
        }
    )
