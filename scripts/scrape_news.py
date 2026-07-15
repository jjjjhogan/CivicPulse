"""
Fetch Irvine-area local news via RSS and write CivicPulse signals.

Usage:
    python scripts/scrape_news.py
    python scripts/scrape_news.py --outlet irvine-standard --outlet voice-of-oc
    python scripts/scrape_news.py --max-articles 40 --no-require-category
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scrapers.feed import rebuild_landing_feed  # noqa: E402
from scrapers.news.export import process_news_to_signals  # noqa: E402
from scrapers.news.scrape import NEWS_SOURCES  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch Irvine local news RSS feeds into CivicSignal JSON."
    )
    parser.add_argument(
        "--outlet",
        action="append",
        dest="outlets",
        help="Outlet id or name to include (repeatable). Default: all.",
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=None,
        help="Stop after this many matching articles (across all selected outlets).",
    )
    parser.add_argument(
        "--no-require-category",
        action="store_true",
        help="Keep articles that do not match a civic issue category.",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "data" / "signals" / "news.json"),
        help="Path to write normalized news signals",
    )
    parser.add_argument(
        "--feed",
        default=str(ROOT / "data" / "signals" / "feed.json"),
        help="Path to landing-page feed JSON",
    )
    parser.add_argument(
        "--no-feed",
        action="store_true",
        help="Skip updating the landing-page feed",
    )
    parser.add_argument(
        "--list-outlets",
        action="store_true",
        help="Print available outlets and exit",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.list_outlets:
        for source in NEWS_SOURCES:
            print(f"{source['id']}\t{source['name']}\t{source['feed']}")
        return

    count, signals = process_news_to_signals(
        args.output,
        outlets=args.outlets,
        max_articles=args.max_articles,
        require_category_match=not args.no_require_category,
    )
    print(f"Wrote {count} news signals -> {args.output}")
    for signal in signals[:15]:
        cats = ", ".join(signal.categories) or "(none)"
        print(f"  [{signal.outlet}] {signal.title} ({cats})")
    if count > 15:
        print(f"  … and {count - 15} more")

    if not args.no_feed:
        feed_count = rebuild_landing_feed(ROOT / "data" / "signals", Path(args.feed))
        print(f"Rebuilt landing-page feed with {feed_count} signals -> {args.feed}")


if __name__ == "__main__":
    main()
