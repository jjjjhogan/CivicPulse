"""
Compare pond / signal JSON / active SQLite counts per source.

Usage:
    python scripts/verify_signal_counts.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import func, select  # noqa: E402

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models import Signal  # noqa: E402
from backend.pool import SOURCE_FILES, read_pond  # noqa: E402
from backend.signals_import import _read_signal_rows  # noqa: E402
from backend.config import SIGNALS_DIR  # noqa: E402


def main() -> None:
    init_db()
    report = {}
    db = SessionLocal()
    try:
        for source in SOURCE_FILES:
            pond_n = len(read_pond(source))
            sig_n = len(_read_signal_rows(SIGNALS_DIR / f"{source}.json"))
            active = db.scalar(
                select(func.count())
                .select_from(Signal)
                .where(Signal.source == source, Signal.archived_at.is_(None))
            )
            archived = db.scalar(
                select(func.count())
                .select_from(Signal)
                .where(Signal.source == source, Signal.archived_at.is_not(None))
            )
            report[source] = {
                "pond": pond_n,
                "signals_json": sig_n,
                "db_active": int(active or 0),
                "db_archived": int(archived or 0),
                "ok": pond_n >= sig_n >= int(active or 0),
            }
    finally:
        db.close()
    print(json.dumps(report, indent=2))
    if not all(v["ok"] for v in report.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
