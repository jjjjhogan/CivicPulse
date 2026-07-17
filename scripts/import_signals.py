"""
Import existing data/signals/*.json into SQLite.

Usage:
    python scripts/import_signals.py
    python scripts/import_signals.py --replace
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models import Signal  # noqa: E402
from backend.signals_import import import_signals_from_dir  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Import JSON signals into SQLite.")
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing signal rows before import.",
    )
    args = parser.parse_args()

    if args.replace:
        init_db()
        db = SessionLocal()
        try:
            deleted = db.query(Signal).delete()
            db.commit()
            print(f"Deleted {deleted} existing signal rows.")
        finally:
            db.close()

    totals = import_signals_from_dir()
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    main()
