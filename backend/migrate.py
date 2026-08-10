"""Additive SQLite schema migrations (Path B)."""

from __future__ import annotations

from sqlalchemy import inspect, text

from backend.db import get_engine
from backend.stable_id import compute_stable_id

TARGET_VERSION = 1


def _current_version(conn) -> int:
    insp = inspect(conn)
    if "schema_version" not in insp.get_table_names():
        return 0
    row = conn.execute(
        text("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
    ).fetchone()
    return int(row[0]) if row else 0


def _column_names(conn, table: str) -> set[str]:
    insp = inspect(conn)
    if table not in insp.get_table_names():
        return set()
    return {col["name"] for col in insp.get_columns(table)}


def migrate_to_v1(conn) -> None:
    cols = _column_names(conn, "signals")
    if not cols:
        return
    for name, ddl in (
        ("stable_id", "ALTER TABLE signals ADD COLUMN stable_id VARCHAR(64)"),
        ("updated_at", "ALTER TABLE signals ADD COLUMN updated_at DATETIME"),
        ("last_seen_at", "ALTER TABLE signals ADD COLUMN last_seen_at DATETIME"),
        ("archived_at", "ALTER TABLE signals ADD COLUMN archived_at DATETIME"),
        ("ingest_job_id", "ALTER TABLE signals ADD COLUMN ingest_job_id INTEGER"),
    ):
        if name not in cols:
            conn.execute(text(ddl))

    rows = conn.execute(
        text("SELECT id, source, url, title, body, stable_id, metadata FROM signals")
    ).fetchall()
    seen: set[str] = set()
    for row in rows:
        sid = row.stable_id
        if not sid:
            meta = row.metadata
            if isinstance(meta, str):
                import json

                try:
                    meta = json.loads(meta)
                except json.JSONDecodeError:
                    meta = {}
            sid = compute_stable_id(
                row.source or "",
                row.url or "",
                row.title or "",
                row.body or "",
                metadata=meta if isinstance(meta, dict) else None,
            )
        if sid in seen:
            sid = f"{sid}-{row.id}"
        seen.add(sid)
        conn.execute(
            text("UPDATE signals SET stable_id = :sid WHERE id = :id"),
            {"sid": sid, "id": row.id},
        )


    conn.execute(
        text("CREATE UNIQUE INDEX IF NOT EXISTS uq_signals_stable_id ON signals (stable_id)")
    )
    conn.execute(
        text("CREATE INDEX IF NOT EXISTS ix_signals_ingest_job_id ON signals (ingest_job_id)")
    )


def run_migrations(*, create_tables: bool = False) -> int:
    """Apply pending migrations. Returns current schema version."""
    if create_tables:
        from backend.db import init_db

        init_db(run_migrate=False)

    eng = get_engine()
    with eng.begin() as conn:
        version = _current_version(conn)
        conn.execute(
            text(
                "CREATE TABLE IF NOT EXISTS schema_version ("
                "id INTEGER PRIMARY KEY, "
                "version INTEGER NOT NULL, "
                "applied_at DATETIME"
                ")"
            )
        )
        if version < 1:
            migrate_to_v1(conn)
            conn.execute(
                text(
                    "INSERT INTO schema_version (version, applied_at) "
                    "VALUES (1, CURRENT_TIMESTAMP)"
                )
            )
            version = 1
    return version
