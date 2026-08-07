"""Restore curated civic housing signals that were dropped from live JSON.

Pulls known-good posts from an older git revision (not orphan DB recovery),
skips listing ads / lifestyle fluff, and merges into data/signals/*.json.
Re-run scripts/reprocess_signals.py afterward to classify + sync DB.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS_DIR = ROOT / "data" / "signals"
REFS = ("HEAD~10", "HEAD~15", "HEAD~20")

# Prefer posts that are useful for a housing Research archive demo.
# Exclude ads, dorm chatter, casual mortgage jokes, hero fluff, flock FP.
# One-liner TikTok "rent is scary" posts are gold=none — do not seed those.
KEEP_URL_SUBSTRINGS = (
    "a_love_letter_to_capitalism",
)

# Explicit rejects even if they appeared under housing historically.
REJECT_URL_SUBSTRINGS = (
    "newstarjennynam",  # listing ad
    "wow_happy_tory",  # hero story
    "do_irvine_residents_feel_safer",  # flock cameras FP
    "globalgags7",  # Irvine Company meme
    "kimiaskravings",  # mortgage lol
    "skylarensign_",  # rented homes / youth event
    "irenek4ng",  # themed housing / dorm
    "1kjaylive",  # lifestyle rent one-liners (gold=none)
)


def _row_key(row: dict) -> tuple:
    return (row.get("source"), row.get("url") or "", row.get("title") or "")


def _load_ref_source(ref: str, source: str) -> list[dict]:
    try:
        raw = subprocess.check_output(
            ["git", "show", f"{ref}:data/signals/{source}.json"],
            cwd=ROOT,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        return []
    return json.loads(raw)


def _wanted(row: dict) -> bool:
    url = row.get("url") or ""
    if any(bad in url for bad in REJECT_URL_SUBSTRINGS):
        return False
    if any(good in url for good in KEEP_URL_SUBSTRINGS):
        return True
    text = f"{row.get('title') or ''} {row.get('body') or ''}".lower()
    # Extra civic landlord / rent-burden phrasing from older scrapes.
    civic_markers = (
        "average rent",
        "rent prices have risen",
        "greedy landlords",
        "housing costs",
        "unhoused",
    )
    return any(marker in text for marker in civic_markers) and "housing" in (
        row.get("categories") or []
    )


def main() -> None:
    added = 0
    for source in ("tiktok", "reddit", "twitter", "news"):
        path = SIGNALS_DIR / f"{source}.json"
        if not path.is_file():
            continue
        current = json.loads(path.read_text(encoding="utf-8"))
        known = {_row_key(row) for row in current}
        for ref in REFS:
            for row in _load_ref_source(ref, source):
                if not _wanted(row):
                    continue
                if _row_key(row) in known:
                    continue
                # Clear stale categories; reprocess will reclassify.
                row = dict(row)
                row["categories"] = []
                meta = dict(row.get("metadata") or {})
                meta.pop("classification", None)
                row["metadata"] = meta
                current.append(row)
                known.add(_row_key(row))
                added += 1
                title = (row.get("title") or "")[:80]
                print(f"+ {source} ({ref}): {title}")
        path.write_text(json.dumps(current, indent=2), encoding="utf-8")
    print(f"Restored {added} housing seed signal(s). Run reprocess_signals.py next.")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
