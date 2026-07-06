"""Convert TikTok scrape results into CivicPulse signals."""

import json
from datetime import datetime, timezone

from scrapers.categories import classify
from scrapers.schema import CivicSignal, timestamp_to_date
from scrapers.tiktok.comments import TikTokComment
from scrapers.tiktok.tags import TikTokTagResult, TikTokVideo


def _truncate(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def comment_to_signal(comment: TikTokComment, video: TikTokVideo) -> CivicSignal:
    categories = classify(f"{comment.text}\n{video.caption}")
    outlet = f"TikTok #{video.tag}" if video.tag else f"TikTok @{video.author or 'unknown'}"
    return CivicSignal(
        source="tiktok",
        outlet=outlet,
        title=_truncate(comment.text),
        body=comment.text,
        url=video.url,
        categories=categories,
        published_utc=timestamp_to_date(comment.scraped_at),
        metadata={
            "author": comment.author,
            "video_author": video.author,
            "tag": video.tag,
            "search_query": comment.search_query,
            "like_count": video.like_count,
            "comment_count": video.comment_count,
        },
    )


def video_caption_to_signal(video: TikTokVideo) -> CivicSignal | None:
    if not video.caption:
        return None
    categories = classify(video.caption)
    if not categories:
        return None
    return CivicSignal(
        source="tiktok",
        outlet=f"TikTok @{video.author or 'unknown'}",
        title=_truncate(video.caption),
        body=video.caption,
        url=video.url,
        categories=categories,
        published_utc=timestamp_to_date(video.scraped_at),
        metadata={"tag": video.tag, "content_type": "video_caption"},
    )


def tag_results_to_signals(
    results: list[TikTokTagResult],
    *,
    civic_only: bool = True,
) -> list[CivicSignal]:
    signals: list[CivicSignal] = []

    for result in results:
        for video in result.videos:
            caption_signal = video_caption_to_signal(video)
            if caption_signal and (not civic_only or caption_signal.categories):
                signals.append(caption_signal)

            for comment in video.comments:
                signal = comment_to_signal(comment, video)
                if civic_only and not signal.categories:
                    continue
                signals.append(signal)

    return signals


def comments_to_signals(
    comments: list[TikTokComment],
    *,
    video_url: str,
    outlet: str,
    civic_only: bool = True,
) -> list[CivicSignal]:
    video = TikTokVideo(url=video_url, tag="", tag_url="", author=outlet.removeprefix("TikTok @"))
    signals = [comment_to_signal(comment, video) for comment in comments]
    if civic_only:
        signals = [signal for signal in signals if signal.categories]
    return signals


def write_signals_json(
    signals: list[CivicSignal],
    output_path: str,
    *,
    landing_page: bool = False,
) -> int:
    if landing_page:
        payload = [signal.to_landing_page_dict() for signal in signals]
    else:
        payload = [signal.to_dict() for signal in signals]

    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return len(signals)


def write_ingest_manifest(output_path: str, *, sources: list[str]) -> None:
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sources": sources,
        "landing_page_feed": "data/signals/feed.json",
    }
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)
