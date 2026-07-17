"""Import / sync CivicSignal JSON files into the Signal table."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import SIGNALS_DIR
from backend.db import SessionLocal, init_db
from backend.models import Signal

SOURCE_FILES = ("tiktok", "reddit", "twitter", "news")


def _read_signal_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def upsert_signals(session: Session, rows: list[dict]) -> tuple[int, int]:
    """Insert or update signals. Returns (inserted, updated)."""
    inserted = 0
    updated = 0
    for row in rows:
        source = (row.get("source") or "").strip()
        title = row.get("title") or ""
        url = row.get("url") or ""
        if not source:
            continue

        existing = session.scalar(
            select(Signal).where(
                Signal.source == source,
                Signal.url == url,
                Signal.title == title,
            )
        )
        categories = row.get("categories") or []
        if not isinstance(categories, list):
            categories = []
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}

        if existing is None:
            session.add(
                Signal(
                    source=source,
                    outlet=row.get("outlet") or "",
                    title=title,
                    body=row.get("body") or "",
                    url=url,
                    categories=categories,
                    published_utc=row.get("published_utc") or "",
                    extra=metadata,
                )
            )
            inserted += 1
        else:
            existing.outlet = row.get("outlet") or ""
            existing.body = row.get("body") or ""
            existing.categories = categories
            existing.published_utc = row.get("published_utc") or ""
            existing.extra = metadata
            updated += 1

    return inserted, updated


def import_signals_from_dir(
    signals_dir: Path | None = None,
    *,
    sources: tuple[str, ...] = SOURCE_FILES,
) -> dict:
    """Load data/signals/<source>.json into SQLite. Returns counts."""
    init_db()
    directory = signals_dir or SIGNALS_DIR
    totals = {"inserted": 0, "updated": 0, "by_source": {}}

    db = SessionLocal()
    try:
        for source in sources:
            rows = _read_signal_rows(directory / f"{source}.json")
            inserted, updated = upsert_signals(db, rows)
            db.commit()
            totals["inserted"] += inserted
            totals["updated"] += updated
            totals["by_source"][source] = {
                "rows": len(rows),
                "inserted": inserted,
                "updated": updated,
            }
    finally:
        db.close()

    return totals


def sync_signals_after_scrape(source: str | None = None) -> dict:
    """Re-import JSON signal files after a scrape finishes."""
    if source in {"irvine-news", "news"}:
        sources = ("news",)
    elif source in SOURCE_FILES:
        sources = (source,)
    else:
        sources = SOURCE_FILES
    return import_signals_from_dir(sources=sources)
