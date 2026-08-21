"""Remove TikTok videos (and their comments) that carry a given hashtag.

Use this for geo contamination (e.g. #orangecountynews pulling Orange County, FL).

Why not Firestore-only: upsert after scrape/reprocess sets archived_at=None, so
the rows come back unless they are also gone from data/signals and data/raw.

Usage:
    python scripts/purge_tiktok_hashtag.py --hashtag florida --apply
    python scripts/purge_tiktok_hashtag.py --hashtag orlando --author wesh2orlando --author wfla8 --apply
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scrapers.feed import rebuild_landing_feed  # noqa: E402


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm_url(url: str) -> str:
    return (url or "").split("?", 1)[0].rstrip("/").lower()


def _norm_tag(tag: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (tag or "").lower().lstrip("#"))


def _norm_handle(handle: str) -> str:
    return re.sub(r"[^a-z0-9._]+", "", (handle or "").lower().lstrip("@"))


def _url_handle(url: str) -> str:
    match = re.search(r"tiktok\.com/@([^/]+)", url or "", re.I)
    return _norm_handle(match.group(1)) if match else ""


def _hashtag_in_text(text: str, hashtag: str) -> bool:
    needle = _norm_tag(hashtag)
    if not needle:
        return False
    return bool(re.search(rf"(?:^|[^a-z0-9])#{needle}(?:[^a-z0-9]|$)", text or "", re.I))


def video_has_hashtag(hashtags: list | None, caption: str, extra: str, hashtag: str) -> bool:
    needle = _norm_tag(hashtag)
    for tag in hashtags or []:
        if _norm_tag(str(tag)) == needle:
            return True
    blob = " ".join(part for part in (caption, extra) if part)
    return _hashtag_in_text(blob, hashtag)


def signal_marks_video(row: dict, hashtags: list[str], authors: set[str]) -> bool:
    md = row.get("metadata") or {}
    extra = " ".join(
        [
            str(row.get("title") or ""),
            str(row.get("body") or ""),
            str(row.get("outlet") or ""),
            str(md.get("tag") or ""),
            str(md.get("search_query") or ""),
        ]
    )
    if any(video_has_hashtag(md.get("hashtags") or [], extra, "", tag) for tag in hashtags):
        return True
    handles = {
        _norm_handle(str(md.get("video_author") or "")),
        _norm_handle(str(md.get("author") or "")),
        _url_handle(str(row.get("url") or "")),
        _norm_handle(str(row.get("outlet") or "").replace("TikTok", "")),
    }
    return bool(authors and (handles & authors))


def _read_json(path: Path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def _backup(path: Path, stamp: str) -> Path | None:
    if not path.is_file():
        return None
    dest_dir = ROOT / "data" / "backups"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{path.parent.name}_{path.stem}_{stamp}{path.suffix}"
    shutil.copy2(path, dest)
    return dest


def collect_bad_urls(
    signals: list[dict],
    raw: dict | None,
    hashtags: list[str],
    authors: set[str],
) -> set[str]:
    urls: set[str] = set()
    for row in signals:
        if signal_marks_video(row, hashtags, authors) and row.get("url"):
            urls.add(_norm_url(row["url"]))
    if not isinstance(raw, dict):
        return urls
    for tag in raw.get("tags") or []:
        for video in tag.get("videos") or []:
            caption = str(video.get("caption") or "")
            extra = " ".join(
                [
                    str(video.get("tag") or ""),
                    " ".join(f"#{t}" for t in (video.get("hashtags") or [])),
                ]
            )
            handle = _norm_handle(str(video.get("author") or ""))
            hit = any(
                video_has_hashtag(video.get("hashtags") or [], caption, extra, htag)
                for htag in hashtags
            )
            if authors and (handle in authors or _url_handle(str(video.get("url") or "")) in authors):
                hit = True
            if hit and video.get("url"):
                urls.add(_norm_url(video["url"]))
    return urls


def filter_signals(rows: list[dict], bad_urls: set[str]) -> tuple[list[dict], list[dict]]:
    kept, removed = [], []
    for row in rows:
        if _norm_url(row.get("url") or "") in bad_urls:
            removed.append(row)
        else:
            kept.append(row)
    return kept, removed


def filter_raw(raw: dict, bad_urls: set[str]) -> tuple[dict, int]:
    dropped = 0
    for tag in raw.get("tags") or []:
        videos = tag.get("videos") or []
        keep = []
        for video in videos:
            if _norm_url(video.get("url") or "") in bad_urls:
                dropped += 1
            else:
                keep.append(video)
        tag["videos"] = keep
        tag["video_count"] = len(keep)
    raw["tag_count"] = len(raw.get("tags") or [])
    return raw, dropped


def archive_firestore(stable_ids: list[str]) -> int:
    from backend.firestore import get_firestore_client

    db = get_firestore_client()
    coll = db.collection("signals")
    now = _utcnow_iso()
    archived = 0
    batch = db.batch()
    ops = 0
    for sid in stable_ids:
        if not sid:
            continue
        batch.update(coll.document(sid), {"archived_at": now, "updated_at": now})
        ops += 1
        archived += 1
        if ops >= 400:
            batch.commit()
            batch = db.batch()
            ops = 0
    if ops:
        batch.commit()
    return archived


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purge TikTok videos by hashtag and/or author.")
    parser.add_argument(
        "--hashtag",
        action="append",
        default=[],
        help="Hashtag to strip (repeatable), e.g. orlando",
    )
    parser.add_argument(
        "--author",
        action="append",
        default=[],
        help="TikTok handle to strip (repeatable), e.g. wfla8",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write files and archive Firestore docs. Default is dry-run.",
    )
    return parser.parse_args()


def firestore_ids_for_urls(bad_urls: set[str], authors: set[str]) -> list[str]:
    from backend.firestore import get_firestore_client

    db = get_firestore_client()
    ids = []
    for doc in db.collection("signals").where("source", "==", "tiktok").stream():
        data = doc.to_dict() or {}
        if data.get("archived_at"):
            continue
        url = str(data.get("url") or "")
        md = data.get("metadata") or {}
        handle = _norm_handle(str(md.get("video_author") or data.get("outlet") or ""))
        if _norm_url(url) in bad_urls or (authors and handle in authors) or (
            authors and _url_handle(url) in authors
        ):
            ids.append(doc.id)
    return ids


def main() -> None:
    args = parse_args()
    hashtags = [h for h in (args.hashtag or []) if h.strip()]
    authors = {_norm_handle(a) for a in (args.author or []) if a.strip()}
    if not hashtags and not authors:
        raise SystemExit("Provide --hashtag and/or --author")

    signals_path = ROOT / "data" / "signals" / "tiktok.json"
    raw_path = ROOT / "data" / "raw" / "tiktok_scrape.json"
    pond_path = ROOT / "data" / "pool" / "tiktok.json"

    signals = _read_json(signals_path) if signals_path.is_file() else []
    raw = _read_json(raw_path) if raw_path.is_file() else None
    pond = _read_json(pond_path) if pond_path.is_file() else []

    bad_urls = collect_bad_urls(
        signals, raw if isinstance(raw, dict) else None, hashtags, authors,
    )
    kept_signals, removed_signals = filter_signals(signals, bad_urls)
    pond_kept, pond_removed = filter_signals(pond, bad_urls) if pond else ([], [])

    print("hashtags", [f"#{_norm_tag(h)}" for h in hashtags] or "-")
    print("authors", sorted(authors) or "-")
    print(f"videos marked: {len(bad_urls)}")
    print(f"signals: {len(signals)} -> keep {len(kept_signals)}, drop {len(removed_signals)}")
    print(f"pond:    {len(pond)} -> keep {len(pond_kept)}, drop {len(pond_removed)}")
    if isinstance(raw, dict):
        _, raw_dropped = filter_raw(json.loads(json.dumps(raw)), bad_urls)
        print(f"raw videos dropped: {raw_dropped}")

    if not args.apply:
        print("dry-run only; re-run with --apply to write + archive Firestore")
        return

    stamp = _utcnow()
    for path in (signals_path, raw_path, pond_path):
        dest = _backup(path, stamp)
        if dest:
            print(f"backup {dest.relative_to(ROOT)}")

    _write_json(signals_path, kept_signals)
    if pond:
        _write_json(pond_path, pond_kept)
    if isinstance(raw, dict):
        raw, _ = filter_raw(raw, bad_urls)
        _write_json(raw_path, raw)

    feed_n = rebuild_landing_feed(ROOT / "data" / "signals", ROOT / "data" / "signals" / "feed.json")
    print(f"rebuilt feed.json ({feed_n} rows)")

    ids = firestore_ids_for_urls(bad_urls, authors)
    archived = archive_firestore(ids)
    print(f"Firestore archived_at set on {archived} tiktok docs")


if __name__ == "__main__":
    main()
