"""Known local / regional news handles used to boost TikTok civic confidence."""

from __future__ import annotations

# Lowercase handles without leading @. Keep focused on LA / OC newsrooms.
TRUSTED_NEWS_HANDLES = frozenset(
    {
        "ktlanews",
        "abc7",
        "abc7la",
        "nbcla",
        "cbsla",
        "foxla",
        "ocregister",
        "latimes",
        "voiceofoc",
        "spectrumnews1",
        "spectrumnews",
        "ocfeed",
        "irvinestandard",
        "irvineweekly",
        "cityofirvine",
        "irvinepolice",
        "ocfa",
        "ochumanrelations",
        "pbssoocal",
        "calmatters",
        "lacity",
        "lapdhq",
        "daily_pilot",
        "dailypilot",
        "ocweekly",
    }
)


def normalize_handle(author: str) -> str:
    return (author or "").lstrip("@").strip().lower()


def is_trusted_news_outlet(author: str) -> bool:
    handle = normalize_handle(author)
    if not handle:
        return False
    if handle in TRUSTED_NEWS_HANDLES:
        return True
    # Common local-news handle patterns.
    return (
        handle.endswith("news")
        or handle.startswith("abc")
        or "newschannel" in handle
        or handle.endswith("abc")
    )
