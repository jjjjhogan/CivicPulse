"""
Apply additive SQLite schema migrations for Path B durability.

Usage:
    python scripts/migrate_db.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.db import SessionLocal, configure_engine  # noqa: E402
from backend.migrate import TARGET_VERSION, run_migrations  # noqa: E402
from backend.models import Signal  # noqa: E402


def main() -> None:
    configure_engine()
    version = run_migrations(create_tables=True)
    print(f"schema_version={version} (target={TARGET_VERSION})")
    db = SessionLocal()
    try:
        missing = (
            db.query(Signal)
            .filter((Signal.stable_id == None) | (Signal.stable_id == ""))  # noqa: E711
            .count()
        )
        print(f"signals_missing_stable_id={missing}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
