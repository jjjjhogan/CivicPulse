"""
Load signals NDJSON into Firestore (emulator or live project).

Usage:
    # Terminal 1: firebase emulators:start --only firestore
    # Terminal 2:
    set FIRESTORE_EMULATOR_HOST=127.0.0.1:8081
    set DATA_BACKEND=firestore
    python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson
    python scripts/import_signals_firestore.py -i data/exports/signals.ndjson
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.firestore import get_firestore_client  # noqa: E402
from backend.store_firestore import FirestoreSignalStore  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Import NDJSON signals into Firestore.")
    parser.add_argument(
        "-i",
        "--input",
        default=str(ROOT / "data" / "exports" / "signals.ndjson"),
        help="Input NDJSON path from export_signals_ndjson.py",
    )
    args = parser.parse_args()

    if not os.environ.get("FIRESTORE_EMULATOR_HOST"):
        cred = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        project = os.environ.get("FIREBASE_PROJECT_ID") or os.environ.get(
            "GOOGLE_CLOUD_PROJECT"
        )
        if not project or not cred:
            print(
                "Real Firestore needs FIREBASE_PROJECT_ID and "
                "GOOGLE_APPLICATION_CREDENTIALS in the environment "
                "(or set FIRESTORE_EMULATOR_HOST for local emulator).",
                file=sys.stderr,
            )
            raise SystemExit(2)
        if not Path(cred).is_file():
            raise SystemExit(f"Service-account file not found: {cred}")

    path = Path(args.input)
    if not path.is_file():
        raise SystemExit(f"Input not found: {path}")

    rows: list[dict] = []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if isinstance(row, dict):
                # Normalize export shape → store upsert shape
                if row.get("stable_id") and "metadata" not in row:
                    row["metadata"] = {}
                rows.append(row)

    store = FirestoreSignalStore(get_firestore_client())
    counts = store.upsert_many(rows)
    print(json.dumps({"rows": len(rows), **counts}, indent=2))


if __name__ == "__main__":
    main()
