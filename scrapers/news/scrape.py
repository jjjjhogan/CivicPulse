"""RSS ingestion for Irvine-area local news outlets."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from time import mktime

import feedparser
from bs4 import BeautifulSoup

from scrapers.classifier import classify_signal

# "citywide" outlets are treated as Irvine-focused; "county" outlets are
# filtered down to Irvine-relevant stories via LOCAL_TERMS.
NEWS_SOURCES = [
    {
        "id": "irvine-standard",
        "name": "Irvine Standard",
        "feed": "https://irvinestandard.com/feed/",
        "scope": "citywide",
    },
    {
        "id": "irvine-weekly",
        "name": "Irvine Weekly",
        "feed": "https://irvineweekly.com/feed/",
        "scope": "citywide",
    },
    {
        "id": "voice-of-oc",
        "name": "Voice of OC",
        "feed": "https://voiceofoc.org/feed/",
        "scope": "county",
    },
]

LOCAL_TERMS = ["irvine"]


def _matches(keyword: str, text: str) -> bool:
    return re.search(r"\b" + re.escape(keyword), text) is not None


def is_local(text: str) -> bool:
    text_lower = text.lower()
    return any(_matches(term, text_lower) for term in LOCAL_TERMS)


def entry_full_text(entry) -> str:
    """Title + summary + full article body, with HTML stripped."""
    parts = [entry.get("title", ""), entry.get("summary", "")]
    parts.extend(block.get("value", "") for block in entry.get("content", []))
    return BeautifulSoup("\n".join(parts), "html5lib").get_text(" ")


def entry_timestamp(entry) -> str:
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return ""
    return datetime.fromtimestamp(mktime(parsed), tz=timezone.utc).strftime("%Y-%m-%d")


def _strip_summary(html: str) -> str:
    if not html:
        return ""
    return BeautifulSoup(html, "html5lib").get_text(" ").strip()


def fetch_news(
    *,
    outlets: list[str] | None = None,
    max_articles: int | None = None,
    require_category_match: bool = True,
) -> list[dict]:
    """
    Pull articles from configured RSS feeds.

    `outlets` may be outlet ids (`irvine-standard`) or display names
    (`Irvine Standard`). When omitted, all sources are fetched.
    """
    selected = NEWS_SOURCES
    if outlets:
        wanted = {value.strip().lower() for value in outlets if value and value.strip()}
        selected = [
            source
            for source in NEWS_SOURCES
            if source["id"] in wanted or source["name"].lower() in wanted
        ]
        if not selected:
            raise ValueError(
                "No matching outlets. Valid ids: "
                + ", ".join(source["id"] for source in NEWS_SOURCES)
            )

    records: list[dict] = []
    for source in selected:
        feed = feedparser.parse(source["feed"])
        for entry in feed.entries:
            title = entry.get("title", "")
            summary = _strip_summary(entry.get("summary", ""))
            text = entry_full_text(entry)

            if source["scope"] == "county" and not is_local(text):
                continue

            classification = classify_signal(text)
            if require_category_match and not classification.categories:
                continue

            records.append(
                {
                    "source": "news",
                    "outlet": source["name"],
                    "outlet_id": source["id"],
                    "title": title,
                    "body": summary or title,
                    "url": entry.get("link", ""),
                    "published_utc": entry_timestamp(entry),
                    "categories": classification.categories,
                    "metadata": {"classification": classification.to_dict()},
                }
            )
            if max_articles is not None and len(records) >= max_articles:
                return records

    return records
