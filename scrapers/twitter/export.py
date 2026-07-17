"""Convert Twitter/X scrape results into CivicPulse signals."""

import json
from datetime import datetime

from scrapers.classifier import classify_signal
from scrapers.schema import CivicSignal


def _truncate(text: str, limit: int = 140) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3] + "..."


def _tweet_url(tweet: dict) -> str:
    author = tweet.get("author") or {}
    handle = author.get("handle") or "i"
    tweet_id = tweet.get("id") or ""
    return f"https://x.com/{handle}/status/{tweet_id}"


def _published_date(tweet: dict) -> str:
    created = tweet.get("createdAt") or ""
    if not created:
        return ""
    try:
        parsed = datetime.strptime(created, "%a %b %d %H:%M:%S %z %Y")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return created[:10]


def tweet_to_signal(tweet: dict, *, query: str) -> CivicSignal:
    text = (tweet.get("text") or "").strip()
    author = tweet.get("author") or {}
    handle = author.get("handle") or "unknown"
    counts = tweet.get("counts") or {}
    classification = classify_signal(text)

    return CivicSignal(
        source="twitter",
        outlet=f"@{handle}",
        title=_truncate(text),
        body=text,
        url=_tweet_url(tweet),
        categories=classification.categories,
        published_utc=_published_date(tweet),
        metadata={
            "author_name": author.get("name") or handle,
            "tweet_id": tweet.get("id"),
            "conversation_id": tweet.get("conversationId"),
            "search_query": query,
            "in_reply_to": tweet.get("inReplyToStatusId"),
            "likes": counts.get("likes"),
            "reposts": counts.get("reposts"),
            "replies": counts.get("replies"),
            "views": counts.get("views"),
            "verified": author.get("verified"),
            "classification": classification.to_dict(),
        },
    )


def scrape_payload_to_signals(
    payload: dict,
    *,
    civic_only: bool = True,
    skip_replies: bool = False,
) -> list[CivicSignal]:
    query = payload.get("query") or ""
    signals: list[CivicSignal] = []

    for tweet in payload.get("tweets") or []:
        if skip_replies and tweet.get("inReplyToStatusId"):
            continue
        signal = tweet_to_signal(tweet, query=query)
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
    skip_replies: bool = False,
) -> tuple[int, int]:
    with open(input_path, encoding="utf-8") as handle:
        payload = json.load(handle)

    all_signals = scrape_payload_to_signals(
        payload,
        civic_only=False,
        skip_replies=skip_replies,
    )
    civic_signals = [s for s in all_signals if s.categories] if civic_only else all_signals

    write_signals_json(civic_signals, output_path)
    if include_all_path:
        write_signals_json(all_signals, include_all_path)

    return len(all_signals), len(civic_signals)
