"""
Re-run classification from giant-pool ponds (or legacy signals JSON).

Reads data/pool/{source}.json when present, otherwise data/signals/{source}.json.
Rewrites data/signals/{source}.json, rebuilds feed, upserts SQLite.
Does NOT prune/archive unless explicitly requested.

Usage:
    python scripts/reprocess_signals.py
    python scripts/reprocess_signals.py --source reddit
    python scripts/reprocess_signals.py --archive-missing
    python scripts/reprocess_signals.py --prune
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scrapers.feed import rebuild_landing_feed  # noqa: E402
from scrapers.reprocess import reclassify_row, thread_consensus  # noqa: E402
from backend.config import POOL_DIR, SIGNALS_DIR  # noqa: E402
from backend.db_backup import backup_database, require_backup  # noqa: E402
from backend.pool import merge_into_pond, pond_path, read_pond  # noqa: E402
from backend.stable_id import ensure_stable_id  # noqa: E402

SOURCES = ("tiktok", "reddit", "twitter", "news")
ALL_FILES = {"reddit": "reddit_all.json", "twitter": "twitter_all.json"}


def _read_rows(path: Path) -> list[dict] | None:
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write_rows(path: Path, rows: list[dict] | dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)


def _load_corpus(source: str) -> list[dict] | None:
    """Prefer pond; fall back to signals + optional *_all merge into memory."""
    pond_rows = read_pond(source)
    if pond_rows:
        return pond_rows

    path = SIGNALS_DIR / f"{source}.json"
    rows = _read_rows(path)
    if rows is None:
        return None

    all_name = ALL_FILES.get(source)
    if all_name:
        all_rows = _read_rows(SIGNALS_DIR / all_name) or []
        by_id: dict[str, dict] = {}
        for row in rows + all_rows:
            if not isinstance(row, dict):
                continue
            if not (row.get("source") or "").strip():
                row["source"] = source
            by_id[ensure_stable_id(row)] = row
        return list(by_id.values())
    return rows


def summarize(source: str, signal_rows: list[dict], pond_n: int) -> None:
    methods: dict[str, int] = {}
    scored = []
    for row in signal_rows:
        cls = (row.get("metadata") or {}).get("classification") or {}
        methods[cls.get("method", "?")] = methods.get(cls.get("method", "?"), 0) + 1
        if row.get("categories"):
            scored.append(cls.get("confidence") or 0)
    avg = sum(scored) / len(scored) if scored else 0
    parts = [f"{count} {method}" for method, count in sorted(methods.items(), key=lambda kv: -kv[1])]
    print(
        f"{source:8s} pond={pond_n:4d} signals={len(signal_rows):4d} · "
        f"avg confidence {avg:.2f} · {', '.join(parts)}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reclassify from ponds into signal JSON + SQLite."
    )
    parser.add_argument("--source", choices=SOURCES, help="Only reprocess one source")
    parser.add_argument(
        "--no-rescue",
        action="store_true",
        help="Ignored when ponds exist; kept for CLI compatibility.",
    )
    parser.add_argument(
        "--archive-missing",
        action="store_true",
        help="Soft-archive DB rows for processed sources missing from new signal JSON.",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="Hard-delete DB rows for processed sources missing from signal JSON (requires backup).",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow archive/prune when a signal JSON file is empty.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = [args.source] if args.source else list(SOURCES)

    processed: list[str] = []
    for source in sources:
        corpus = _load_corpus(source)
        if corpus is None:
            print(f"{source:8s} no pond or signals JSON, skipped")
            continue

        # Keep cumulative pond in sync when we fell back to signals/*_all.
        if not pond_path(source).is_file():
            merge_into_pond(source, corpus)

        for row in corpus:
            if not (row.get("source") or "").strip():
                row["source"] = source
            ensure_stable_id(row)

        consensus = thread_consensus(corpus) if source == "tiktok" else None
        for row in corpus:
            reclassify_row(row, consensus)

        # Persist full reclassified corpus back into the pond (categories may change).
        merge_into_pond(source, corpus)
        pond_n = len(read_pond(source))

        signal_rows = [row for row in read_pond(source) if row.get("categories")]
        for row in signal_rows:
            ensure_stable_id(row)
        _write_rows(SIGNALS_DIR / f"{source}.json", signal_rows)
        processed.append(source)
        summarize(source, signal_rows, pond_n)

    if not processed:
        return

    feed_count = rebuild_landing_feed(SIGNALS_DIR, SIGNALS_DIR / "feed.json")
    _write_rows(
        SIGNALS_DIR / "manifest.json",
        {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "sources": processed,
            "landing_page_feed": "data/signals/feed.json",
        },
    )
    print(f"Rebuilt landing-page feed with {feed_count} signals")

    from backend.signals_import import (
        archive_missing_signals,
        import_signals_from_dir,
        prune_orphan_signals,
    )

    if args.archive_missing or args.prune:
        backup_path = require_backup()
        print(f"DB backup: {backup_path.relative_to(ROOT)}")
    else:
        backup_path = backup_database()
        if backup_path:
            print(f"DB backup: {backup_path.relative_to(ROOT)}")
        else:
            print("DB backup: skipped (no SQLite file yet)")

    totals = import_signals_from_dir(sources=tuple(processed))
    archived = 0
    pruned = 0
    if args.archive_missing:
        archived = archive_missing_signals(
            sources=tuple(processed), allow_empty=args.allow_empty
        )
    if args.prune:
        pruned = prune_orphan_signals(
            sources=tuple(processed), allow_empty=args.allow_empty
        )
    print(
        f"Synced SQLite: inserted={totals['inserted']} updated={totals['updated']} "
        f"archived={archived} pruned={pruned}"
    )


if __name__ == "__main__":
    main()
