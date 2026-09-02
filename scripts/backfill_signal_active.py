"""
Backfill Firestore signals.active from archived_at.

Run once after deploying the active+created_at indexes:

    python scripts/backfill_signal_active.py
    python scripts/backfill_signal_active.py --apply
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill signals.active on Firestore.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write updates. Default is dry-run.",
    )
    args = parser.parse_args()

    if not os.environ.get("FIREBASE_PROJECT_ID") and not os.environ.get(
        "GOOGLE_CLOUD_PROJECT"
    ):
        print("Set FIREBASE_PROJECT_ID (and credentials) first.")
        sys.exit(1)

    from backend.firestore import get_firestore_client

    db = get_firestore_client()
    coll = db.collection("signals")
    updated = 0
    scanned = 0
    batch = db.batch()
    ops = 0
    for doc in coll.stream():
        scanned += 1
        data = doc.to_dict() or {}
        should_be_active = not bool(data.get("archived_at"))
        if data.get("active") is should_be_active:
            continue
        updated += 1
        if not args.apply:
            continue
        batch.update(doc.reference, {"active": should_be_active})
        ops += 1
        if ops >= 400:
            batch.commit()
            batch = db.batch()
            ops = 0
    if args.apply and ops:
        batch.commit()
    mode = "applied" if args.apply else "dry-run"
    print(f"{mode}: scanned={scanned} need_update={updated}")


if __name__ == "__main__":
    main()
