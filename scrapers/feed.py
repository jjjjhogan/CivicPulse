"""Rebuild landing-page feed from normalized signal JSON files."""

from __future__ import annotations

import json
from pathlib import Path


def rebuild_landing_feed(
    signals_dir: Path,
    output_path: Path,
    *,
    sources: tuple[str, ...] = ("tiktok", "reddit", "twitter", "news"),
) -> int:
    feed: list[dict] = []
    for source in sources:
        path = signals_dir / f"{source}.json"
        if not path.is_file():
            continue
        with open(path, encoding="utf-8") as handle:
            rows = json.load(handle)
        for row in rows:
            feed.append(
                {
                    "outlet": row.get("outlet", ""),
                    "title": row.get("title", ""),
                    "categories": row.get("categories", []),
                    "published_utc": row.get("published_utc", ""),
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(feed, handle, indent=2)
    return len(feed)
