"""Stable signal / pond identity for upsert and Firestore doc ids."""

from __future__ import annotations

import hashlib
from urllib.parse import urlsplit, urlunsplit


def normalize_url(url: str) -> str:
    """Light normalization: strip, drop trailing slash, lowercase host."""
    raw = (url or "").strip()
    if not raw:
        return ""
    try:
        parts = urlsplit(raw)
    except ValueError:
        return raw.rstrip("/")
    if not parts.scheme and not parts.netloc:
        return raw.rstrip("/")
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or ""
    return urlunsplit((parts.scheme.lower(), netloc, path, parts.query, ""))


def _platform_fragment(metadata: dict | None) -> str:
    if not isinstance(metadata, dict):
        return ""
    for key in ("comment_id", "post_id", "tweet_id", "id"):
        value = metadata.get(key)
        if value is not None and str(value).strip():
            return f"{key}:{value}"
    return ""


def compute_stable_id(
    source: str,
    url: str = "",
    title: str = "",
    body: str = "",
    metadata: dict | None = None,
) -> str:
    """Return a 40-char hex id suitable as a Firestore document id.

    Identity is source + normalized URL, plus a fragment so multiple comments
    on the same TikTok/video URL stay distinct. Prefer platform ids in metadata;
    otherwise fingerprint the body (not title) so truncation does not churn ids.
    """
    src = (source or "").strip().lower()
    norm = normalize_url(url)
    fragment = _platform_fragment(metadata)
    if not fragment and (body or title):
        # Prefer body (title truncates); fall back to title when body empty.
        fragment = hashlib.sha1((body or title or "").encode("utf-8")).hexdigest()[:16]

    if norm:
        material = f"{src}\n{norm}"
        if fragment:
            material = f"{material}\n{fragment}"
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
    else:
        material = f"{src}\n{title or ''}|{body or ''}"
        digest = hashlib.sha1(material.encode("utf-8")).hexdigest()
    return digest[:40]


def ensure_stable_id(row: dict) -> str:
    """Set stable_id on row (and metadata.stable_id); return it."""
    existing = (row.get("stable_id") or "").strip()
    meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    if not existing:
        existing = (meta.get("stable_id") or "").strip()
    if not existing:
        existing = compute_stable_id(
            row.get("source") or "",
            row.get("url") or "",
            row.get("title") or "",
            row.get("body") or "",
            metadata=meta if isinstance(meta, dict) else None,
        )
    row["stable_id"] = existing
    if not isinstance(row.get("metadata"), dict):
        row["metadata"] = {}
    row["metadata"]["stable_id"] = existing
    return existing
