"""Convert Reddit scrape results into CivicPulse signals."""

import json
from datetime import datetime

from scrapers.classifier import classify_signal
from scrapers.schema import CivicSignal


def _truncate(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def _post_text(post: dict) -> str:
    parts = [post.get("title") or "", post.get("previewText") or ""]
    return "\n".join(part.strip() for part in parts if part and part.strip())


def _published_date(post: dict) -> str:
    created = post.get("createdAt") or ""
    if created:
        return created[:10]
    return ""


def post_to_signal(post: dict, *, subreddit: str, query: str) -> CivicSignal:
    body = _post_text(post)
    classification = classify_signal(body)
    prefixed = post.get("subredditPrefixed") or f"r/{subreddit}"
    return CivicSignal(
        source="reddit",
        outlet=prefixed,
        title=_truncate(post.get("title") or body),
        body=body,
        url=post.get("permalink") or post.get("url") or "",
        categories=classification.categories,
        published_utc=_published_date(post),
        metadata={
            "author": post.get("author") or "unknown",
            "post_id": post.get("id"),
            "score": post.get("score"),
            "comment_count": post.get("commentCount"),
            "search_query": query,
            "flair": post.get("flair"),
            "classification": classification.to_dict(),
        },
    )


def scrape_payload_to_signals(
    payload: dict,
    *,
    civic_only: bool = True,
) -> list[CivicSignal]:
    subreddit = payload.get("subredditFilter") or payload.get("subreddit") or "unknown"
    query = payload.get("query") or ""
    if not query and payload.get("queries"):
        query = "+".join(payload["queries"])
    signals: list[CivicSignal] = []

    items = list(payload.get("items") or [])
    if not items:
        for scrape in payload.get("scrapes") or []:
            items.extend(scrape.get("items") or [])

    for post in items:
        signal = post_to_signal(post, subreddit=subreddit, query=query)
        if civic_only and not signal.categories:
            continue
        signals.append(signal)

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


def process_scrape_file(
    input_path: str,
    output_path: str,
    *,
    civic_only: bool = True,
    include_all_path: str | None = None,
) -> tuple[int, int]:
    with open(input_path, encoding="utf-8") as handle:
        payload = json.load(handle)

    all_signals = scrape_payload_to_signals(payload, civic_only=False)
    civic_signals = [s for s in all_signals if s.categories] if civic_only else all_signals

    write_signals_json(civic_signals, output_path)
    if include_all_path:
        write_signals_json(all_signals, include_all_path)

    return len(all_signals), len(civic_signals)
