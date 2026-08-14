"""Research signal matching — shared between routes and job runner."""

from __future__ import annotations

import re


def match_signals(
    signals: list[dict],
    categories: list[str],
    keywords: list[str],
) -> list[dict]:
    """Find signals matching given categories and/or keywords.

    Returns a list of dicts with signal_id, match_reason, and score.
    """
    research_cats = set(categories or [])
    research_kws = [kw.lower() for kw in (keywords or []) if kw.strip()]

    hits = []
    for signal in signals:
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
