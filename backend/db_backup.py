"""SQLite backup helpers for CivicPulse.

Copy data/civicpulse.db before destructive sync/prune so orphan cleanup
cannot wipe history without a recoverable snapshot.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB = ROOT / "data" / "civicpulse.db"
DEFAULT_BACKUP_DIR = ROOT / "data" / "backups"


def backup_database(
    db_path: Path | None = None,
    backup_dir: Path | None = None,
) -> Path | None:
    """Copy the live DB to data/backups/civicpulse_YYYYMMDD.db.

    Same-day re-runs overwrite the dated file (one snapshot per calendar day).
    Returns the backup path, or None if the source DB is missing.
    """
    source = db_path or DEFAULT_DB
    if not source.is_file():
        return None

    dest_dir = backup_dir or DEFAULT_BACKUP_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    dest = dest_dir / f"civicpulse_{stamp}.db"
    shutil.copy2(source, dest)
    return dest
