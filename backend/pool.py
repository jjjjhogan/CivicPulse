"""Giant-pool pond helpers: cumulative JSON per source."""

from __future__ import annotations

import json
from pathlib import Path

from backend.config import POOL_DIR, SIGNALS_DIR
from backend.stable_id import ensure_stable_id

SOURCE_FILES = ("tiktok", "reddit", "twitter", "news")
ALL_FILES = {"reddit": "reddit_all.json", "twitter": "twitter_all.json"}


def pond_path(source: str, pool_dir: Path | None = None) -> Path:
    return (pool_dir or POOL_DIR) / f"{source}.json"


def read_pond(source: str, pool_dir: Path | None = None) -> list[dict]:
    path = pond_path(source, pool_dir)
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def write_pond(source: str, rows: list[dict], pool_dir: Path | None = None) -> Path:
    directory = pool_dir or POOL_DIR
    directory.mkdir(parents=True, exist_ok=True)
    path = pond_path(source, directory)
    for row in rows:
        ensure_stable_id(row)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2)
    return path


def merge_into_pond(
    source: str,
    incoming: list[dict],
    pool_dir: Path | None = None,
) -> dict:
    """Upsert incoming rows into the pond by stable_id. Never deletes pond rows.

    Returns counts: {inserted, updated, total}.
    """
    existing = read_pond(source, pool_dir)
    by_id: dict[str, dict] = {}
    for row in existing:
        sid = ensure_stable_id(row)
        by_id[sid] = row

    inserted = 0
    updated = 0
    for row in incoming:
        if not isinstance(row, dict):
            continue
        if not (row.get("source") or "").strip():
            row = {**row, "source": source}
        sid = ensure_stable_id(row)
        if sid in by_id:
            prev = by_id[sid]
            prev.update({k: v for k, v in row.items() if k != "stable_id"})
            ensure_stable_id(prev)
            by_id[sid] = prev
            updated += 1
        else:
            by_id[sid] = row
            inserted += 1

    write_pond(source, list(by_id.values()), pool_dir)
    return {"inserted": inserted, "updated": updated, "total": len(by_id)}


def bootstrap_ponds(
    *,
    pool_dir: Path | None = None,
    signals_dir: Path | None = None,
    sources: tuple[str, ...] = SOURCE_FILES,
) -> dict:
    """Seed ponds from signals JSON + *_all.json reject pools."""
    sig_dir = signals_dir or SIGNALS_DIR
    totals: dict[str, dict] = {}
    for source in sources:
        incoming: list[dict] = []
        civic_path = sig_dir / f"{source}.json"
        if civic_path.is_file():
            with open(civic_path, encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, list):
                incoming.extend(row for row in data if isinstance(row, dict))
        all_name = ALL_FILES.get(source)
        if all_name:
            all_path = sig_dir / all_name
            if all_path.is_file():
                with open(all_path, encoding="utf-8") as handle:
                    data = json.load(handle)
                if isinstance(data, list):
                    incoming.extend(row for row in data if isinstance(row, dict))
        for row in incoming:
            if not (row.get("source") or "").strip():
                row["source"] = source
        totals[source] = merge_into_pond(source, incoming, pool_dir)
    return totals
