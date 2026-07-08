"""
Process a Reddit scrape JSON export into CivicPulse signals.

Usage:
    python scripts/process_reddit_scrape.py
    python scripts/process_reddit_scrape.py --input data/raw/reddit_scrape.json
    python scripts/process_reddit_scrape.py --include-all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scrapers.feed import rebuild_landing_feed  # noqa: E402
from scrapers.reddit.export import process_scrape_file  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Reddit scrape JSON to CivicSignal output.")
    parser.add_argument(
        "--input",
        default=str(ROOT / "data" / "raw" / "reddit_scrape.json"),
        help="Path to raw Reddit scrape JSON",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "signals" / "reddit.json"),
        help="Path to write normalized signals",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Also write all posts (including non-civic) to reddit_all.json",
    )
    parser.add_argument(
        "--feed",
        default=str(ROOT / "data" / "signals" / "feed.json"),
        help="Path to landing-page feed JSON (merged with existing TikTok signals)",
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

    include_all_path = None
    if args.include_all:
        include_all_path = str(Path(args.output).with_name("reddit_all.json"))

    total, civic = process_scrape_file(
        str(input_path),
        args.output,
        civic_only=True,
        include_all_path=include_all_path,
    )
    print(f"Processed {total} Reddit posts -> {civic} civic signals -> {args.output}")

    if not args.no_feed:
        count = rebuild_landing_feed(ROOT / "data" / "signals", Path(args.feed))
        print(f"Rebuilt landing-page feed with {count} signals -> {args.feed}")


if __name__ == "__main__":
    main()
