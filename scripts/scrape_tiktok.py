"""
Entry point for TikTok civic-issue comment scraping.

Test one video:
    python scripts/scrape_tiktok.py --video-url "https://www.tiktok.com/@user/video/123"

Scrape tag pages and export landing-page-ready signals:
    python scripts/scrape_tiktok.py --tag-url "https://www.tiktok.com/tag/irvine" --max-videos 3
"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Windows job/console hosts often use cp1252; TikTok captions include emoji.
for _stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(_stream, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass

from scrapers.categories import CivicIssueCategory
from scrapers.feed import rebuild_landing_feed
from scrapers.tiktok.comments import scrape_comments_for_area, scrape_comments_from_video
from scrapers.tiktok.config import TikTokScrapeConfig
from scrapers.tiktok.export import (
    comments_to_signals,
    tag_results_to_signals,
    write_ingest_manifest,
    write_signals_json,
)
from scrapers.tiktok.tags import (
    dedupe_raw_payload,
    load_raw_payload,
    merge_tag_results_into_payload,
    scrape_tags,
    tag_results_from_payload,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape TikTok comments for civic issues in a geographic area."
    )
    parser.add_argument("--video-url", help="Scrape comments from one TikTok video URL")
    parser.add_argument(
        "--tag-url",
        action="append",
        dest="tag_urls",
        help="Scrape videos and comments from a TikTok tag page (repeatable)",
    )
    parser.add_argument("--city", help="Target city, e.g. Los Angeles")
    parser.add_argument("--state", default="CA", help="Target state abbreviation")
    parser.add_argument("--neighborhood", help="Optional neighborhood within the city")
    parser.add_argument(
        "--categories",
        nargs="+",
        choices=[c.value for c in CivicIssueCategory],
        default=[c.value for c in CivicIssueCategory],
        help="Civic issue categories to search for",
    )
    parser.add_argument("--max-videos", type=int, default=3)
    parser.add_argument("--max-comments", type=int, default=25)
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--output",
        default="data/raw/tiktok_scrape.json",
        help="Path to write raw scrape JSON",
    )
    parser.add_argument(
        "--signals-output",
        default="data/signals/tiktok.json",
        help="Path to write normalized CivicSignal JSON",
    )
    parser.add_argument(
        "--feed-output",
        default="data/signals/feed.json",
        help="Path to landing-page feed JSON (rebuilt with all sources)",
    )
    parser.add_argument(
        "--include-all-comments",
        action="store_true",
        help="Include comments that do not match a civic issue category",
    )
    return parser.parse_args()


def _write_raw_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _write_signal_exports(args: argparse.Namespace, signals) -> None:
    signals_path = Path(args.signals_output)
    feed_path = Path(args.feed_output)
    signals_path.parent.mkdir(parents=True, exist_ok=True)
    feed_path.parent.mkdir(parents=True, exist_ok=True)

    signal_count = write_signals_json(signals, str(signals_path), landing_page=False)
    write_ingest_manifest(str(signals_path.parent / "manifest.json"), sources=["tiktok"])
    feed_count = rebuild_landing_feed(ROOT / "data" / "signals", feed_path)
    print(f"Saved {signal_count} normalized signals to {signals_path}")
    print(f"Rebuilt landing-page feed with {feed_count} signals -> {feed_path}")


def main() -> None:
    args = parse_args()

    if not args.video_url and not args.tag_urls and not args.city:
        raise SystemExit("Provide one of: --video-url, --tag-url, or --city.")

    output_path = Path(args.output)
    civic_only = not args.include_all_comments

    if args.tag_urls:
        existing = load_raw_payload(output_path)
        existing, removed = dedupe_raw_payload(existing)
        if removed:
            print(f"Removed {removed} duplicate video(s) from {output_path}")

        skip_urls = {
            (video.get("url") or "").split("?", 1)[0].rstrip("/")
            for tag in existing.get("tags") or []
            for video in tag.get("videos") or []
            if video.get("url")
        }
        if skip_urls:
            print(f"Skipping {len(skip_urls)} already-scraped video URL(s)")

        new_results = scrape_tags(
            args.tag_urls,
            max_videos=args.max_videos,
            max_comments_per_video=args.max_comments,
            headless=args.headless,
            skip_urls=skip_urls,
        )
        payload = merge_tag_results_into_payload(existing, new_results)
        _write_raw_json(output_path, payload)

        all_results = tag_results_from_payload(payload)
        signals = tag_results_to_signals(all_results, civic_only=civic_only)
        _write_signal_exports(args, signals)

        new_videos = sum(len(result.videos) for result in new_results)
        total_videos = sum(len(result.videos) for result in all_results)
        comment_count = sum(
            len(video.comments) for result in all_results for video in result.videos
        )
        print(
            f"Saved {new_videos} new videos ({total_videos} total, {comment_count} comments) "
            f"from {len(all_results)} tags to {output_path}"
        )
    elif args.video_url:
        comments = scrape_comments_from_video(
            args.video_url,
            max_comments=args.max_comments,
            headless=args.headless,
        )
        _write_raw_json(output_path, [asdict(comment) for comment in comments])
        author = args.video_url.split("/@")[1].split("/")[0]
        signals = comments_to_signals(
            comments,
            video_url=args.video_url,
            outlet=f"TikTok @{author}",
            civic_only=civic_only,
        )
        _write_signal_exports(args, signals)
        print(f"Saved {len(comments)} comments to {output_path}")
    else:
        config = TikTokScrapeConfig(
            city=args.city,
            state=args.state,
            neighborhood=args.neighborhood,
            categories=[CivicIssueCategory(c) for c in args.categories],
            max_videos_per_query=args.max_videos,
            max_comments_per_video=args.max_comments,
            headless=args.headless,
        )
        comments = scrape_comments_for_area(config)
        _write_raw_json(output_path, [asdict(comment) for comment in comments])
        signals = comments_to_signals(
            comments,
            video_url="",
            outlet=f"TikTok search: {config.location_label()}",
            civic_only=civic_only,
        )
        _write_signal_exports(args, signals)
        print(f"Saved {len(comments)} comments to {output_path}")


if __name__ == "__main__":
    main()
