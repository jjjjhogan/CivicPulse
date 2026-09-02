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


def mapped_listen_sources(listen_sources: list[str] | None) -> set[str] | None:
    if not listen_sources:
        return None
    return {SOURCE_MAP.get(s, s) for s in listen_sources}


def signal_snapshot(signal: dict) -> dict:
    """Compact signal fields stored on research hits (avoids N+1 reads)."""
    body = signal.get("body") or ""
    if len(body) > 280:
        body = body[:277] + "..."
    return {
        "id": signal.get("id"),
        "stable_id": signal.get("stable_id") or signal.get("id"),
        "source": signal.get("source") or "",
        "outlet": signal.get("outlet") or "",
        "title": signal.get("title") or "",
        "body": body,
        "url": signal.get("url") or "",
        "categories": list(signal.get("categories") or []),
        "published_utc": signal.get("published_utc") or "",
    }


# Hard cap so Research archive match never streams the full lake unbounded.
RESEARCH_CANDIDATE_CAP = 5000


def load_candidate_signals(signal_store, listen_sources: list[str] | None = None) -> list[dict]:
    """Load signals for archive match — prefer per-source queries when listen is set."""
    allowed = mapped_listen_sources(listen_sources)
    if allowed is None:
        page = signal_store.list_signals(limit=RESEARCH_CANDIDATE_CAP)
        return page["signals"] if isinstance(page, dict) else page
    rows: list[dict] = []
    per_source = max(1, RESEARCH_CANDIDATE_CAP // max(1, len(allowed)))
    for src in sorted(allowed):
        rows.extend(
            signal_store.list_signals_by_source(src, limit=per_source)
        )
        if len(rows) >= RESEARCH_CANDIDATE_CAP:
            break
    return rows[:RESEARCH_CANDIDATE_CAP]


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

    Returns hit dicts with signal_id, match_reason, score, and embedded signal snapshot.
    """
    research_cats = set(categories or [])
    research_kws = [kw.lower() for kw in (keywords or []) if kw.strip()]

    allowed_sources = mapped_listen_sources(listen_sources)

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
                "signal": signal_snapshot(signal),
            })

    hits.sort(key=lambda h: -h["score"])
    return hits
