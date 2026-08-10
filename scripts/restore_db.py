"""
Restore civicpulse.db from a backup file.

Usage:
    python scripts/restore_db.py --from data/backups/civicpulse_YYYYMMDD_HHMMSS.db --force
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.config import DB_PATH  # noqa: E402
from backend.db_backup import resolve_sqlite_path  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Restore SQLite DB from a backup copy.")
    parser.add_argument("--from", dest="source", required=True, help="Backup .db path")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite the active DB without interactive confirm.",
    )
    parser.add_argument(
        "--to",
        dest="dest",
        default=None,
        help="Destination DB path (default: active DATABASE_URL / data/civicpulse.db)",
    )
    args = parser.parse_args()

    source = Path(args.source)
    if not source.is_file():
        raise SystemExit(f"Backup not found: {source}")
    if not args.force:
        raise SystemExit("Refusing to overwrite without --force")

    dest = Path(args.dest) if args.dest else (resolve_sqlite_path() or DB_PATH)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    print(f"Restored {source} -> {dest}")


if __name__ == "__main__":
    main()
