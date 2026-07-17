"""Scrape job runners — wrap existing CLI scrapers as background jobs."""

from __future__ import annotations

import json
import subprocess
import sys
import threading

from backend.config import (
    NEWS_DEFAULTS,
    PROCESS_REDDIT,
    PROCESS_TWITTER,
    RAW_DIR,
    ROOT,
    SCRAPE_NEWS,
    SCRAPE_TIKTOK,
    TIKTOK_DEFAULTS,
)
from backend.db import SessionLocal
from backend.models import ScrapeJob, utcnow

_job_lock = threading.Lock()
_running_job_id: int | None = None


def _news_outlet_ids() -> list[str]:
    sys.path.insert(0, str(ROOT))
    from scrapers.news.scrape import NEWS_SOURCES  # noqa: WPS433

    return [source["id"] for source in NEWS_SOURCES]


def build_tiktok_command(payload: dict) -> list[str]:
    mode = payload.get("mode", "tags")
    cmd = [sys.executable, str(SCRAPE_TIKTOK)]

    if mode == "video":
        video_url = (payload.get("video_url") or "").strip()
        if not video_url:
            raise ValueError("video_url is required for video mode.")
        cmd.extend(["--video-url", video_url])
    elif mode == "city":
        city = (payload.get("city") or "").strip()
        if not city:
            raise ValueError("city is required for city mode.")
        cmd.extend(["--city", city])
        state = (payload.get("state") or "CA").strip()
        if state:
            cmd.extend(["--state", state])
        neighborhood = (payload.get("neighborhood") or "").strip()
        if neighborhood:
            cmd.extend(["--neighborhood", neighborhood])
        categories = payload.get("categories") or []
        if categories:
            cmd.append("--categories")
            cmd.extend(categories)
    else:
        tag_urls = [url.strip() for url in payload.get("tag_urls", []) if url.strip()]
        if not tag_urls:
            raise ValueError("At least one tag URL is required for tag mode.")
        for tag_url in tag_urls:
            cmd.extend(["--tag-url", tag_url])

    max_videos = int(payload.get("max_videos", TIKTOK_DEFAULTS["max_videos"]))
    max_comments = int(payload.get("max_comments", TIKTOK_DEFAULTS["max_comments"]))
    cmd.extend(["--max-videos", str(max_videos)])
    cmd.extend(["--max-comments", str(max_comments)])

    if payload.get("headless", False):
        cmd.append("--headless")
    if payload.get("include_all_comments"):
        cmd.append("--include-all-comments")

    return cmd


def build_news_command(payload: dict) -> list[str]:
    cmd = [sys.executable, str(SCRAPE_NEWS)]
    outlets = payload.get("outlets")
    if outlets is None:
        outlets = list(NEWS_DEFAULTS["outlets"])
    outlets = [str(item).strip() for item in outlets if str(item).strip()]
    if not outlets:
        raise ValueError("Select at least one news outlet.")
    for outlet in outlets:
        cmd.extend(["--outlet", outlet])

    max_articles = payload.get("max_articles", NEWS_DEFAULTS["max_articles"])
    if max_articles is not None and str(max_articles).strip() != "":
        cmd.extend(["--max-articles", str(int(max_articles))])

    require_match = payload.get(
        "require_category_match", NEWS_DEFAULTS["require_category_match"]
    )
    if not require_match:
        cmd.append("--no-require-category")

    return cmd


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def build_import_command(*, source: str, payload: dict) -> list[str]:
    if source == "reddit":
        raw_name = "reddit_scrape.json"
        process_script = PROCESS_REDDIT
    elif source == "twitter":
        raw_name = "twitter_scrape.json"
        process_script = PROCESS_TWITTER
    else:
        raise ValueError(f"Import source '{source}' is not supported.")

    raw_path = RAW_DIR / raw_name
    _write_json(raw_path, payload)
    return [
        sys.executable,
        str(process_script),
        "--input",
        str(raw_path),
        "--include-all",
    ]


def build_command(source: str, settings: dict) -> list[str]:
    if source == "tiktok":
        merged = {**TIKTOK_DEFAULTS, **(settings or {})}
        return build_tiktok_command(merged)

    if source in {"irvine-news", "news"}:
        merged = {**NEWS_DEFAULTS, **(settings or {})}
        return build_news_command(merged)

    if source in {"reddit", "twitter"}:
        payload = (settings or {}).get("payload")
        if payload is None:
            raise ValueError("settings.payload is required for import jobs.")
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict):
            raise ValueError("settings.payload must be a JSON object.")
        return build_import_command(source=source, payload=payload)

    raise ValueError(f"Scraper '{source}' is not implemented yet.")


def normalize_source(source: str) -> str:
    if source == "news":
        return "irvine-news"
    return source


def is_job_running() -> bool:
    with _job_lock:
        return _running_job_id is not None


def _run_job(job_id: int, cmd: list[str]) -> None:
    global _running_job_id
    try:
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        log = (result.stdout or "") + (result.stderr or "")
        sync_source = None
        db = SessionLocal()
        try:
            job = db.get(ScrapeJob, job_id)
            if job is None:
                return
            sync_source = job.source
            job.log = log
            job.exit_code = result.returncode
            job.finished_at = utcnow()
            if result.returncode == 0:
                job.status = "completed"
                job.error = None
            else:
                job.status = "failed"
                job.error = f"Scraper exited with code {result.returncode}"
            db.commit()
        finally:
            db.close()

        if result.returncode == 0 and sync_source:
            try:
                from backend.signals_import import sync_signals_after_scrape

                sync_signals_after_scrape(sync_source)
            except Exception as sync_exc:  # noqa: BLE001
                db = SessionLocal()
                try:
                    job = db.get(ScrapeJob, job_id)
                    if job is not None:
                        job.log = (job.log or "") + f"\n[signal sync warning] {sync_exc}"
                        db.commit()
                finally:
                    db.close()
    except Exception as exc:  # noqa: BLE001
        db = SessionLocal()
        try:
            job = db.get(ScrapeJob, job_id)
            if job is not None:
                job.status = "failed"
                job.error = str(exc)
                job.finished_at = utcnow()
                db.commit()
        finally:
            db.close()
    finally:
        with _job_lock:
            if _running_job_id == job_id:
                _running_job_id = None


def start_job(job_id: int, cmd: list[str]) -> bool:
    """Mark job running and spawn worker. Returns False if another job is active."""
    global _running_job_id
    with _job_lock:
        if _running_job_id is not None:
            return False
        _running_job_id = job_id

    db = SessionLocal()
    try:
        job = db.get(ScrapeJob, job_id)
        if job is None:
            with _job_lock:
                _running_job_id = None
            return False
        job.status = "running"
        job.command = " ".join(cmd)
        job.started_at = utcnow()
        job.error = None
        job.log = ""
        job.exit_code = None
        db.commit()
    finally:
        db.close()

    thread = threading.Thread(target=_run_job, args=(job_id, cmd), daemon=True)
    thread.start()
    return True
