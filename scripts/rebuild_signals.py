"""
Rebuild signal exports from an existing raw TikTok scrape, without re-scraping.

Useful after changing CATEGORY_KEYWORDS in scrapers/categories.py:
    python scripts/rebuild_signals.py
    python scripts/rebuild_signals.py --include-all-comments
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scrapers.tiktok.comments import TikTokComment
from scrapers.tiktok.export import (
    tag_results_to_signals,
    write_ingest_manifest,
    write_signals_json,
)
from scrapers.tiktok.tags import TikTokTagResult, TikTokVideo


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Re-run signal classification over an existing raw scrape."
    )
    parser.add_argument("--input", default="data/raw/tiktok_scrape.json")
    parser.add_argument("--signals-output", default="data/signals/tiktok.json")
    parser.add_argument("--feed-output", default="data/signals/feed.json")
    parser.add_argument(
        "--include-all-comments",
        action="store_true",
        help="Include comments that do not match a civic issue category",
    )
    return parser.parse_args()


def load_tag_results(path: Path) -> list[TikTokTagResult]:
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)

    if "tags" not in payload:
        raise SystemExit(
            f"{path} is not a tag scrape (expected top-level 'tags' key). "
            "rebuild_signals.py only supports raw output from tag mode."
        )

    results: list[TikTokTagResult] = []
    for tag_entry in payload["tags"]:
        videos = []
        for video_entry in tag_entry.get("videos", []):
            comments = [
                TikTokComment(**comment) for comment in video_entry.get("comments", [])
            ]
            videos.append(
                TikTokVideo(**{**video_entry, "comments": comments})
            )
        results.append(
            TikTokTagResult(
                tag=tag_entry["tag"],
                tag_url=tag_entry["tag_url"],
                videos=videos,
                scraped_at=tag_entry.get("scraped_at", 0.0),
            )
        )
    return results


def main() -> None:
    args = parse_args()
    results = load_tag_results(Path(args.input))

    video_count = sum(len(result.videos) for result in results)
    comment_count = sum(
        len(video.comments) for result in results for video in result.videos
    )
    print(f"Loaded {video_count} videos and {comment_count} comments from {args.input}")

    signals = tag_results_to_signals(
        results, civic_only=not args.include_all_comments
    )

    signals_path = Path(args.signals_output)
    feed_path = Path(args.feed_output)
    signals_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.parent.mkdir(parents=True, exist_ok=True)

    signal_count = write_signals_json(signals, str(signals_path), landing_page=False)
    feed_count = write_signals_json(signals, str(feed_path), landing_page=True)
    write_ingest_manifest(str(signals_path.parent / "manifest.json"), sources=["tiktok"])

    by_category: dict[str, int] = {}
    for signal in signals:
        for category in signal.categories or ["uncategorized"]:
            by_category[category] = by_category.get(category, 0) + 1

    print(f"Saved {signal_count} normalized signals to {signals_path}")
    print(f"Saved {feed_count} landing-page signals to {feed_path}")
    if by_category:
        print("Signals by category:")
        for category, count in sorted(by_category.items(), key=lambda kv: -kv[1]):
            print(f"  {category}: {count}")


if __name__ == "__main__":
    main()
