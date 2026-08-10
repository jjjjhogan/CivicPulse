"""SQLite backup helpers for CivicPulse."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from backend.config import BACKUP_DIR, DB_PATH, database_url


def resolve_sqlite_path(db_path: Path | None = None) -> Path | None:
    """Return the on-disk SQLite file for the active engine URL, if any."""
    if db_path is not None:
        return db_path
    url = database_url()
    if url.startswith("sqlite:///"):
        return Path(url[len("sqlite:///") :])
    return DB_PATH if DB_PATH.is_file() else None


def backup_database(
    db_path: Path | None = None,
    backup_dir: Path | None = None,
) -> Path | None:
    """Copy the live DB to data/backups/civicpulse_YYYYMMDD_HHMMSS.db.

    Returns the backup path, or None if the source DB is missing.
    """
    source = resolve_sqlite_path(db_path)
    if source is None or not source.is_file():
        return None

    dest_dir = backup_dir or BACKUP_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest = dest_dir / f"civicpulse_{stamp}.db"
    shutil.copy2(source, dest)
    return dest


def require_backup(
    db_path: Path | None = None,
    backup_dir: Path | None = None,
) -> Path:
    """Backup or raise RuntimeError (for destructive ops)."""
    path = backup_database(db_path=db_path, backup_dir=backup_dir)
    if path is None:
        raise RuntimeError("DB backup required but no SQLite database file was found")
    return path
