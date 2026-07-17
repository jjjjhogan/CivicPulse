"""Convert TikTok scrape results into CivicPulse signals."""

from __future__ import annotations

import json
from datetime import datetime, timezone

from scrapers.categories import classify
from scrapers.classifier import classify_signal, inherited_classification
from scrapers.schema import CivicSignal, timestamp_to_date
from scrapers.tiktok.comments import TikTokComment
from scrapers.tiktok.outlets import is_trusted_news_outlet, normalize_handle
from scrapers.tiktok.tags import TikTokTagResult, TikTokVideo


def _truncate(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def video_context_text(video: TikTokVideo) -> str:
    """Caption + hashtags + search tag — the best keyword surface for the video."""
    parts = [video.caption or ""]
    if video.hashtags:
        parts.extend(f"#{tag}" for tag in video.hashtags)
    if video.tag:
        parts.append(f"#{video.tag}")
    return "\n".join(part for part in parts if part and str(part).strip())


def classify_video(video: TikTokVideo) -> list[str]:
    return classify(video_context_text(video))


def comment_to_signal(
    comment: TikTokComment,
    video: TikTokVideo,
    *,
    video_categories: list[str] | None = None,
) -> CivicSignal:
    trusted = is_trusted_news_outlet(video.author)
    video_cats = list(video_categories if video_categories is not None else classify_video(video))
    direct = classify_signal(f"{comment.text}\n{video_context_text(video)}")

    inherited = False
    if direct.categories:
        categories = direct.categories
        classification = direct.to_dict()
    elif video_cats:
        categories = video_cats
        classification = inherited_classification(video_cats)
        inherited = True
    elif trusted:
        # Newsrooms under civic tags: keep reaction comments even when caption
        # scrape failed and the comment itself has no keywords.
        categories = ["public_safety"]
        classification = inherited_classification(categories, outlet_default=True)
        inherited = True
    else:
        categories = []
        classification = direct.to_dict()

    outlet = f"TikTok @{normalize_handle(video.author) or 'unknown'}"
    if video.tag:
        outlet = f"TikTok #{video.tag}"

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
            "content_type": "comment",
            "inherited_from_video": inherited,
            "trusted_outlet": trusted,
            "video_categories": video_cats,
            "hashtags": list(video.hashtags or []),
            "classification": classification,
        },
    )


def video_caption_to_signal(video: TikTokVideo) -> CivicSignal | None:
    direct = classify_signal(video_context_text(video))
    trusted = is_trusted_news_outlet(video.author)
    caption = (video.caption or "").strip()
    weak_default = False

    categories = list(direct.categories)
    classification = direct.to_dict()
    if not categories and trusted and (caption or video.hashtags):
        categories = ["public_safety"]
        classification = inherited_classification(categories, outlet_default=True)
        weak_default = True

    if not categories:
        return None
    if not caption and not video.hashtags:
        return None

    title_source = caption or " ".join(f"#{tag}" for tag in video.hashtags)
    handle = normalize_handle(video.author) or "unknown"
    return CivicSignal(
        source="tiktok",
        outlet=f"TikTok @{handle}",
        title=_truncate(title_source),
        body=caption or title_source,
        url=video.url,
        categories=categories,
        published_utc=timestamp_to_date(video.scraped_at),
        metadata={
            "tag": video.tag,
            "content_type": "video_caption",
            "trusted_outlet": trusted,
            "hashtags": list(video.hashtags or []),
            "weak_trusted_default": weak_default,
            "classification": classification,
        },
    )


def tag_results_to_signals(
    results: list[TikTokTagResult],
    *,
    civic_only: bool = True,
    inherit_video_categories: bool = True,
) -> list[CivicSignal]:
    signals: list[CivicSignal] = []

    for result in results:
        for video in result.videos:
            video_categories = classify_video(video)
            caption_signal = video_caption_to_signal(video)
            if caption_signal and (not civic_only or caption_signal.categories):
                signals.append(caption_signal)

            trusted = is_trusted_news_outlet(video.author)
            for comment in video.comments:
                signal = comment_to_signal(
                    comment,
                    video,
                    video_categories=video_categories if inherit_video_categories else [],
                )
                if civic_only and not signal.categories:
                    continue
                if (
                    civic_only
                    and signal.metadata.get("inherited_from_video")
                    and not video_categories
                    and not trusted
                ):
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
    video = TikTokVideo(
        url=video_url,
        tag="",
        tag_url="",
        author=outlet.removeprefix("TikTok @"),
    )
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
