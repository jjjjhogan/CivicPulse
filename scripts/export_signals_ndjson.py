"""
Export active SQLite signals to NDJSON for Firestore seeding.

Usage:
    python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sqlalchemy import select  # noqa: E402

from backend.db import SessionLocal, init_db  # noqa: E402
from backend.models import Signal  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Export signals to NDJSON.")
    parser.add_argument(
        "-o",
        "--output",
        default=str(ROOT / "data" / "exports" / "signals.ndjson"),
        help="Output NDJSON path",
    )
    parser.add_argument(
        "--include-archived",
        action="store_true",
        help="Include soft-archived rows",
    )
    args = parser.parse_args()

    init_db()
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    db = SessionLocal()
    count = 0
    try:
        q = select(Signal).order_by(Signal.id.asc())
        if not args.include_archived:
            q = q.where(Signal.archived_at.is_(None))
        rows = db.scalars(q).all()
        with open(out, "w", encoding="utf-8") as handle:
            for row in rows:
                doc = {
                    "stable_id": row.stable_id,
                    "sqlite_id": row.id,
                    "source": row.source,
                    "outlet": row.outlet,
                    "title": row.title,
                    "body": row.body,
                    "url": row.url,
                    "categories": row.categories or [],
                    "published_utc": row.published_utc,
                    "metadata": row.extra or {},
                    "ingest_job_id": row.ingest_job_id,
                    "archived_at": row.archived_at.isoformat() if row.archived_at else None,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "last_seen_at": row.last_seen_at.isoformat() if row.last_seen_at else None,
                }
                handle.write(json.dumps(doc, ensure_ascii=False) + "\n")
                count += 1
    finally:
        db.close()
    print(f"Wrote {count} signals -> {out}")


if __name__ == "__main__":
    main()
