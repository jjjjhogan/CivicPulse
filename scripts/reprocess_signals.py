"""
Re-run classification over the existing normalized signal JSON files.

No re-scraping: reads data/signals/*.json, recomputes categories with
scrapers/classifier.py (keywords + model pass), writes richer
metadata.classification (scores/confidence/method), and rescues "missed
stories" — posts in reddit_all.json / twitter_all.json that the keyword
pass dropped but the model (or an updated keyword list) now classifies.

Usage:
    python scripts/reprocess_signals.py
    python scripts/reprocess_signals.py --source reddit
    python scripts/reprocess_signals.py --no-rescue
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

SIGNALS_DIR = ROOT / "data" / "signals"
SOURCES = ("tiktok", "reddit", "twitter", "news")
ALL_FILES = {"reddit": "reddit_all.json", "twitter": "twitter_all.json"}


def _read_rows(path: Path) -> list[dict] | None:
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write_rows(path: Path, rows: list[dict] | dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)


def _row_key(row: dict) -> tuple:
    return (row.get("source"), row.get("published_utc"), row.get("title"))


def rescue_missed(source: str, civic_rows: list[dict]) -> list[dict]:
    """Pull newly-classified posts out of the *_all.json keyword rejects."""
    all_path = SIGNALS_DIR / ALL_FILES[source]
    all_rows = _read_rows(all_path)
    if all_rows is None:
        return []

    known = {_row_key(row) for row in civic_rows}
    recovered: list[dict] = []
    for row in all_rows:
        had_categories = bool(row.get("categories"))
        reclassify_row(row)
        if row.get("categories") and not had_categories and _row_key(row) not in known:
            recovered.append(row)

    _write_rows(all_path, all_rows)
    return recovered


def summarize(source: str, rows: list[dict], recovered: list[dict]) -> None:
    methods: dict[str, int] = {}
    scored = []
    for row in rows:
        cls = (row.get("metadata") or {}).get("classification") or {}
        methods[cls.get("method", "?")] = methods.get(cls.get("method", "?"), 0) + 1
        if row.get("categories"):
            scored.append(cls.get("confidence") or 0)
    avg = sum(scored) / len(scored) if scored else 0
    parts = [f"{count} {method}" for method, count in sorted(methods.items(), key=lambda kv: -kv[1])]
    line = f"{source:8s} {len(rows):4d} signals · avg confidence {avg:.2f} · {', '.join(parts)}"
    if recovered:
        line += f" · +{len(recovered)} recovered from {ALL_FILES[source]}"
    print(line)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reclassify existing signal JSON with confidence scores."
    )
    parser.add_argument("--source", choices=SOURCES, help="Only reprocess one source")
    parser.add_argument(
        "--no-rescue",
        action="store_true",
        help="Skip pulling newly-classified posts out of the *_all.json files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sources = [args.source] if args.source else list(SOURCES)

    processed: list[str] = []
    for source in sources:
        path = SIGNALS_DIR / f"{source}.json"
        rows = _read_rows(path)
        if rows is None:
            print(f"{source:8s} no {path.name}, skipped")
            continue

        consensus = thread_consensus(rows) if source == "tiktok" else None
        for row in rows:
            reclassify_row(row, consensus)

        recovered = []
        if not args.no_rescue and source in ALL_FILES:
            recovered = rescue_missed(source, rows)
            rows.extend(recovered)

        _write_rows(path, rows)
        processed.append(source)
        summarize(source, rows, recovered)

    if processed:
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

        # Keep SQLite as source of truth for the dashboard API.
        from backend.signals_import import import_signals_from_dir

        totals = import_signals_from_dir(sources=tuple(processed))
        print(
            f"Synced SQLite: inserted={totals['inserted']} updated={totals['updated']}"
        )


if __name__ == "__main__":
    main()
