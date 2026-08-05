"""Reclassify stored CivicSignal rows (shared by CLI and tests)."""

from __future__ import annotations

from scrapers.classifier import (
    MIN_INHERIT_WORDS,
    _content_words,
    classify_signal,
    inherited_classification,
)


def signal_text(row: dict) -> str:
    """Best classification surface we can rebuild from a stored signal."""
    meta = row.get("metadata") or {}
    parts = [row.get("title") or "", row.get("body") or ""]
    parts.extend(f"#{tag}" for tag in meta.get("hashtags") or [])
    if meta.get("tag"):
        parts.append(f"#{meta['tag']}")
    seen: set[str] = set()
    unique = []
    for part in parts:
        cleaned = part.strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique.append(cleaned)
    return "\n".join(unique)


def reclassify_row(row: dict, thread_categories: dict | None = None) -> dict:
    """Update a row's categories + metadata.classification in place."""
    meta = row.setdefault("metadata", {})
    result = classify_signal(signal_text(row))

    consensus = (thread_categories or {}).get(row.get("url") or "")
    if result.categories:
        row["categories"] = result.categories
        meta["classification"] = result.to_dict()
    elif consensus:
        comment_text = (row.get("body") or row.get("title") or "")
        if len(_content_words(comment_text)) < MIN_INHERIT_WORDS:
            row["categories"] = []
            meta["classification"] = result.to_dict()
        else:
            row["categories"] = consensus
            meta["classification"] = inherited_classification(consensus)
    elif meta.get("weak_trusted_default"):
        meta["classification"] = inherited_classification(
            row.get("categories") or [], outlet_default=True
        )
    elif meta.get("inherited_from_video"):
        comment_text = (row.get("body") or row.get("title") or "")
        words = _content_words(comment_text)
        if len(words) < MIN_INHERIT_WORDS:
            row["categories"] = []
            meta["classification"] = result.to_dict()
        else:
            outlet_default = not (meta.get("video_categories") or [])
            meta["classification"] = inherited_classification(
                row.get("categories") or [], outlet_default=outlet_default
            )
    elif row.get("categories"):
        row["categories"] = []
        meta["classification"] = result.to_dict()
    else:
        row["categories"] = []
        meta["classification"] = result.to_dict()
    return row


def thread_consensus(rows: list[dict]) -> dict[str, list[str]]:
    """Classify each TikTok video's stored comment thread as one text."""
    threads: dict[str, list[str]] = {}
    for row in rows:
        url = row.get("url") or ""
        if url:
            threads.setdefault(url, []).append(row.get("body") or row.get("title") or "")
    return {
        url: result.categories
        for url, bodies in threads.items()
        if (result := classify_signal("\n".join(bodies))).categories
    }
