"""Import / sync CivicSignal JSON into the Signal table (stable_id upsert)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import SIGNALS_DIR
from backend.db import SessionLocal, init_db
from backend.models import Signal
from backend.stable_id import ensure_stable_id

SOURCE_FILES = ("tiktok", "reddit", "twitter", "news")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _read_signal_rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def upsert_signals(
    session: Session,
    rows: list[dict],
    *,
    ingest_job_id: int | None = None,
) -> tuple[int, int]:
    """Insert or update signals by stable_id. Returns (inserted, updated)."""
    inserted = 0
    updated = 0
    now = _utcnow()
    pending: dict[str, Signal] = {}
    for row in rows:
        source = (row.get("source") or "").strip()
        if not source:
            continue
        stable_id = ensure_stable_id(row)
        title = row.get("title") or ""
        url = row.get("url") or ""
        categories = row.get("categories") or []
        if not isinstance(categories, list):
            categories = []
        metadata = row.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        metadata = {**metadata, "stable_id": stable_id}

        existing = pending.get(stable_id) or session.scalar(
            select(Signal).where(Signal.stable_id == stable_id)
        )
        if existing is None:
            existing = Signal(
                stable_id=stable_id,
                source=source,
                outlet=row.get("outlet") or "",
                title=title,
                body=row.get("body") or "",
                url=url,
                categories=categories,
                published_utc=row.get("published_utc") or "",
                extra=metadata,
                updated_at=now,
                last_seen_at=now,
                archived_at=None,
                ingest_job_id=ingest_job_id,
            )
            session.add(existing)
            pending[stable_id] = existing
            inserted += 1
        else:
            existing.source = source
            existing.outlet = row.get("outlet") or ""
            existing.title = title
            existing.body = row.get("body") or ""
            existing.url = url
            existing.categories = categories
            existing.published_utc = row.get("published_utc") or ""
            existing.extra = metadata
            existing.updated_at = now
            existing.last_seen_at = now
            if ingest_job_id is not None:
                existing.ingest_job_id = ingest_job_id
            # Re-appearing in an export un-archives.
            existing.archived_at = None
            pending[stable_id] = existing
            updated += 1

    return inserted, updated


def import_signals_from_dir(
    signals_dir: Path | None = None,
    *,
    sources: tuple[str, ...] = SOURCE_FILES,
    ingest_job_id: int | None = None,
) -> dict:
    """Load data/signals/<source>.json into the active backend. Returns counts."""
    from backend.config import DATA_BACKEND

    directory = signals_dir or SIGNALS_DIR
    totals = {"inserted": 0, "updated": 0, "by_source": {}}

    if DATA_BACKEND == "firestore":
        from backend.firestore import get_firestore_client
        from backend.store_firestore import FirestoreSignalStore

        store = FirestoreSignalStore(get_firestore_client())
        for source in sources:
            rows = _read_signal_rows(directory / f"{source}.json")
            counts = store.upsert_many(rows, ingest_job_id=ingest_job_id)
            totals["inserted"] += counts["inserted"]
            totals["updated"] += counts["updated"]
            totals["by_source"][source] = {
                "rows": len(rows),
                "inserted": counts["inserted"],
                "updated": counts["updated"],
            }
        return totals

    init_db()
    db = SessionLocal()
    try:
        for source in sources:
            rows = _read_signal_rows(directory / f"{source}.json")
            inserted, updated = upsert_signals(db, rows, ingest_job_id=ingest_job_id)
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
    """Re-import JSON signal files after a scrape finishes (upsert only)."""
    if source in {"irvine-news", "news"}:
        sources = ("news",)
    elif source in SOURCE_FILES:
        sources = (source,)
    else:
        sources = SOURCE_FILES
    return import_signals_from_dir(sources=sources)


def _json_stable_ids(signals_dir: Path, sources: tuple[str, ...]) -> set[str]:
    keys: set[str] = set()
    for source in sources:
        for row in _read_signal_rows(signals_dir / f"{source}.json"):
            if not (row.get("source") or "").strip():
                row = {**row, "source": source}
            keys.add(ensure_stable_id(row))
    return keys


def _assert_signal_files_ok(
    signals_dir: Path,
    sources: tuple[str, ...],
    *,
    allow_empty: bool,
) -> None:
    for source in sources:
        path = signals_dir / f"{source}.json"
        if not path.is_file():
            raise RuntimeError(f"Missing signal file for archive/prune: {path}")
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, list):
            raise RuntimeError(f"Signal file is not a JSON list: {path}")
        if not data and not allow_empty:
            raise RuntimeError(
                f"Signal file is empty ({path.name}); pass allow_empty=True / --allow-empty to proceed"
            )


def archive_missing_signals(
    signals_dir: Path | None = None,
    *,
    sources: tuple[str, ...] = SOURCE_FILES,
    allow_empty: bool = False,
) -> int:
    """Soft-archive DB rows for `sources` whose stable_id is absent from JSON.

    SQLite only — Firestore signals are managed via upsert_many.
    """
    from backend.config import DATA_BACKEND

    if DATA_BACKEND == "firestore":
        raise RuntimeError("archive_missing_signals is not supported with Firestore.")
    init_db()
    directory = signals_dir or SIGNALS_DIR
    _assert_signal_files_ok(directory, sources, allow_empty=allow_empty)
    json_ids = _json_stable_ids(directory, sources)
    now = _utcnow()

    db = SessionLocal()
    try:
        rows = db.scalars(
            select(Signal).where(Signal.source.in_(sources), Signal.archived_at.is_(None))
        ).all()
        archived = 0
        for row in rows:
            if row.stable_id not in json_ids:
                row.archived_at = now
                archived += 1
        db.commit()
        return archived
    finally:
        db.close()


def prune_orphan_signals(
    signals_dir: Path | None = None,
    *,
    sources: tuple[str, ...] = SOURCE_FILES,
    allow_empty: bool = False,
) -> int:
    """Hard-delete DB signals for `sources` not present in current JSON files.

    Scoped to `sources` only (never deletes other sources). Prefer soft-archive.
    SQLite only — Firestore signals are managed via upsert_many.
    """
    from backend.config import DATA_BACKEND

    if DATA_BACKEND == "firestore":
        raise RuntimeError("prune_orphan_signals is not supported with Firestore.")
    init_db()
    directory = signals_dir or SIGNALS_DIR
    _assert_signal_files_ok(directory, sources, allow_empty=allow_empty)
    json_ids = _json_stable_ids(directory, sources)

    db = SessionLocal()
    try:
        orphans = [
            row
            for row in db.scalars(select(Signal).where(Signal.source.in_(sources))).all()
            if row.stable_id not in json_ids
        ]
        for row in orphans:
            db.delete(row)
        db.commit()
        return len(orphans)
    finally:
        db.close()
