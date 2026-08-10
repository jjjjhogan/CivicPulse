"""Signal storage interface (SQLite now; Firestore later)."""

from __future__ import annotations

import os
from typing import Protocol

from backend.db import SessionLocal, get_session, init_db
from backend.models import Signal
from backend.signals_import import (
    SOURCE_FILES,
    archive_missing_signals,
    import_signals_from_dir,
    prune_orphan_signals,
    upsert_signals,
)


class SignalStore(Protocol):
    def list_signals(self, *, include_archived: bool = False) -> list[dict]: ...

    def upsert_many(self, rows: list[dict], *, ingest_job_id: int | None = None) -> dict: ...

    def archive_missing(
        self,
        *,
        sources: tuple[str, ...] = SOURCE_FILES,
        allow_empty: bool = False,
        signals_dir=None,
    ) -> int: ...

    def hard_prune(
        self,
        *,
        sources: tuple[str, ...] = SOURCE_FILES,
        allow_empty: bool = False,
        signals_dir=None,
    ) -> int: ...


class SqliteSignalStore:
    def list_signals(self, *, include_archived: bool = False) -> list[dict]:
        db = get_session()
        q = db.query(Signal).order_by(Signal.id.asc())
        if not include_archived:
            q = q.filter(Signal.archived_at.is_(None))
        return [row.to_dict() for row in q.all()]

    def upsert_many(self, rows: list[dict], *, ingest_job_id: int | None = None) -> dict:
        init_db()
        db = SessionLocal()
        try:
            inserted, updated = upsert_signals(db, rows, ingest_job_id=ingest_job_id)
            db.commit()
            return {"inserted": inserted, "updated": updated}
        finally:
            db.close()

    def archive_missing(
        self,
        *,
        sources: tuple[str, ...] = SOURCE_FILES,
        allow_empty: bool = False,
        signals_dir=None,
    ) -> int:
        return archive_missing_signals(
            signals_dir, sources=sources, allow_empty=allow_empty
        )

    def hard_prune(
        self,
        *,
        sources: tuple[str, ...] = SOURCE_FILES,
        allow_empty: bool = False,
        signals_dir=None,
    ) -> int:
        return prune_orphan_signals(
            signals_dir, sources=sources, allow_empty=allow_empty
        )

    def import_from_dir(self, signals_dir=None, *, sources: tuple[str, ...] = SOURCE_FILES):
        return import_signals_from_dir(signals_dir, sources=sources)


class FirestoreSignalStore:
    """Stub until Sessions 9–10. Raises until configured."""

    def list_signals(self, *, include_archived: bool = False) -> list[dict]:
        raise RuntimeError("DATA_BACKEND=firestore is not configured yet")

    def upsert_many(self, rows: list[dict], *, ingest_job_id: int | None = None) -> dict:
        raise RuntimeError("DATA_BACKEND=firestore is not configured yet")

    def archive_missing(self, *, sources=SOURCE_FILES, allow_empty=False, signals_dir=None) -> int:
        raise RuntimeError("DATA_BACKEND=firestore is not configured yet")

    def hard_prune(self, *, sources=SOURCE_FILES, allow_empty=False, signals_dir=None) -> int:
        raise RuntimeError("DATA_BACKEND=firestore is not configured yet")


def get_signal_store() -> SignalStore:
    backend = (os.environ.get("DATA_BACKEND") or "sqlite").strip().lower()
    if backend == "firestore":
        return FirestoreSignalStore()
    return SqliteSignalStore()
