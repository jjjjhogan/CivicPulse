"""Research signal matching — shared between routes and job runner."""

from __future__ import annotations

import re


SOURCE_MAP: dict[str, str] = {
    "twitter": "twitter",
    "reddit": "reddit",
    "tiktok": "tiktok",
    "news311": "news",
    "youtube": "youtube",
    "facebook": "facebook",
}


def match_signals(
    signals: list[dict],
    categories: list[str],
    keywords: list[str],
    *,
    listen_sources: list[str] | None = None,
) -> list[dict]:
    """Find signals matching given categories and/or keywords.

    When listen_sources is provided, only signals whose source matches
    one of the listed sources are considered.

    Returns a list of dicts with signal_id, match_reason, and score.
    """
    research_cats = set(categories or [])
    research_kws = [kw.lower() for kw in (keywords or []) if kw.strip()]

    allowed_sources: set[str] | None = None
    if listen_sources:
        allowed_sources = {SOURCE_MAP.get(s, s) for s in listen_sources}

    hits = []
    for signal in signals:
        if allowed_sources is not None:
            sig_source = signal.get("source", "")
            if sig_source not in allowed_sources:
                continue
        reasons = []
        score = 0.0

        signal_cats = set(signal.get("categories") or [])
        overlap = research_cats & signal_cats
        if overlap:
            reasons.append("category:" + ",".join(sorted(overlap)))
            score += 0.5 * len(overlap)

        text = ((signal.get("title") or "") + " " + (signal.get("body") or "")).lower()
        matched_kws = []
        for kw in research_kws:
            if re.search(r"\b" + re.escape(kw), text):
                matched_kws.append(kw)
                score += 0.3

        if matched_kws:
            reasons.append("keyword:" + ",".join(matched_kws))

        if reasons:
            hits.append({
                "signal_id": signal["id"],
                "match_reason": "; ".join(reasons),
                "score": round(score, 2),
            })

    hits.sort(key=lambda h: -h["score"])
    return hits
