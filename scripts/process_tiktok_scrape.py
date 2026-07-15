"""
Re-export TikTok raw scrape JSON into CivicPulse signals (no browser).

Usage:
    python scripts/process_tiktok_scrape.py
    python scripts/process_tiktok_scrape.py --include-all-comments
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scrapers.feed import rebuild_landing_feed  # noqa: E402
from scrapers.tiktok.export import (  # noqa: E402
    tag_results_to_signals,
    write_ingest_manifest,
    write_signals_json,
)
from scrapers.tiktok.tags import (  # noqa: E402
    dedupe_raw_payload,
    load_raw_payload,
    tag_results_from_payload,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert TikTok scrape JSON to CivicSignal output."
    )
    parser.add_argument(
        "--input",
        default=str(ROOT / "data" / "raw" / "tiktok_scrape.json"),
        help="Path to raw TikTok scrape JSON",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "signals" / "tiktok.json"),
        help="Path to write normalized signals",
    )
    parser.add_argument(
        "--feed",
        default=str(ROOT / "data" / "signals" / "feed.json"),
        help="Path to landing-page feed JSON",
    )
    parser.add_argument(
        "--include-all-comments",
        action="store_true",
        help="Keep comments that do not match a civic category",
    )
    parser.add_argument(
        "--no-feed",
        action="store_true",
        help="Skip updating the landing-page feed",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_file():
        raise SystemExit(f"Input file not found: {input_path}")

    payload, removed = dedupe_raw_payload(load_raw_payload(input_path))
    if removed:
        print(f"Removed {removed} duplicate video(s) while loading")

    results = tag_results_from_payload(payload)
    signals = tag_results_to_signals(
        results,
        civic_only=not args.include_all_comments,
    )
    count = write_signals_json(signals, args.output)
    write_ingest_manifest(str(Path(args.output).parent / "manifest.json"), sources=["tiktok"])
    print(f"Wrote {count} TikTok signals -> {args.output}")

    if not args.no_feed:
        feed_count = rebuild_landing_feed(ROOT / "data" / "signals", Path(args.feed))
        print(f"Rebuilt landing-page feed with {feed_count} signals -> {args.feed}")


if __name__ == "__main__":
    main()
