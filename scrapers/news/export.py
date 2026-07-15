"""Convert news scrape results into CivicPulse signals."""

from __future__ import annotations

import json

from scrapers.news.scrape import fetch_news
from scrapers.schema import CivicSignal


def article_to_signal(article: dict) -> CivicSignal:
    return CivicSignal(
        source="news",
        outlet=article.get("outlet") or "Local news",
        title=article.get("title") or "",
        body=article.get("body") or "",
        url=article.get("url") or "",
        categories=list(article.get("categories") or []),
        published_utc=article.get("published_utc") or "",
        metadata={
            "outlet_id": article.get("outlet_id"),
        },
    )


def write_signals_json(signals: list[CivicSignal], output_path: str) -> int:
    payload = [signal.to_dict() for signal in signals]
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return len(signals)


def process_news_to_signals(
    output_path: str,
    *,
    outlets: list[str] | None = None,
    max_articles: int | None = None,
    require_category_match: bool = True,
) -> tuple[int, list[CivicSignal]]:
    articles = fetch_news(
        outlets=outlets,
        max_articles=max_articles,
        require_category_match=require_category_match,
    )
    signals = [article_to_signal(article) for article in articles]
    write_signals_json(signals, output_path)
    return len(signals), signals
