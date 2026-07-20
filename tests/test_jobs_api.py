"""Scrape job API with mocked subprocess (no live network / Selenium)."""

from __future__ import annotations

import subprocess
import time


def _inline_thread(target, args=(), kwargs=None, daemon=None):
    """Run Thread target synchronously so tests don't race."""
    kwargs = kwargs or {}

    class _Immediate:
        def start(self):
            target(*args, **kwargs)

    return _Immediate()


def test_create_and_complete_news_job(auth_client, monkeypatch):
    monkeypatch.setattr(
        "backend.jobs.subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(
            args=a[0] if a else [], returncode=0, stdout="ok\n", stderr=""
        ),
    )
    monkeypatch.setattr("backend.jobs.threading.Thread", _inline_thread)
    monkeypatch.setattr(
        "backend.signals_import.sync_signals_after_scrape",
        lambda source=None: {"inserted": 0, "updated": 0},
    )

    res = auth_client.post(
        "/api/jobs",
        json={
            "source": "irvine-news",
            "settings": {"max_articles": 1, "outlets": ["irvine-standard"]},
        },
    )
    assert res.status_code == 202, res.get_json()
    body = res.get_json()
    job_id = body["id"]
    assert body["status"] in {"running", "completed"}

    # Inline thread finishes before response in most cases; poll briefly.
    status = None
    for _ in range(20):
        poll = auth_client.get(f"/api/jobs/{job_id}")
        assert poll.status_code == 200
        status = poll.get_json()
        if status["status"] in {"completed", "failed"}:
            break
        time.sleep(0.05)

    assert status is not None
    assert status["status"] == "completed"
    assert status["exit_code"] == 0
    assert "ok" in (status.get("log") or "")

    listing = auth_client.get("/api/jobs")
    assert listing.status_code == 200
    jobs = listing.get_json()["jobs"]
    assert any(j["id"] == job_id for j in jobs)


def test_invalid_source(auth_client):
    res = auth_client.post(
        "/api/jobs",
        json={"source": "myspace", "settings": {}},
    )
    assert res.status_code == 400


def test_friendly_scraper_error_chrome():
    from backend.jobs import friendly_scraper_error

    msg = friendly_scraper_error(
        source="tiktok",
        returncode=1,
        log="ChromeUnavailableError: Chrome is not available or ChromeDriver failed to start",
    )
    assert "Chrome is not available" in msg
    assert "TIKTOK_SCRAPE" in msg


def test_friendly_scraper_error_login_wall():
    from backend.jobs import friendly_scraper_error

    msg = friendly_scraper_error(
        source="tiktok",
        returncode=1,
        log="ERROR: tag page #irvine: TikTok login wall is blocking this page.",
    )
    assert "login" in msg.lower()
    assert "TIKTOK_SCRAPE" in msg


def test_failed_tiktok_job_surfaces_login_wall(auth_client, monkeypatch):
    monkeypatch.setattr(
        "backend.jobs.subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(
            args=a[0] if a else [],
            returncode=1,
            stdout="",
            stderr="ERROR: TikTok login wall is blocking this page. See docs/TIKTOK_SCRAPE.md.\n",
        ),
    )
    monkeypatch.setattr("backend.jobs.threading.Thread", _inline_thread)

    res = auth_client.post(
        "/api/jobs",
        json={
            "source": "tiktok",
            "settings": {
                "mode": "tags",
                "tag_urls": ["https://www.tiktok.com/tag/irvine"],
                "max_videos": 1,
                "max_comments": 5,
            },
        },
    )
    assert res.status_code == 202, res.get_json()
    job_id = res.get_json()["id"]

    status = None
    for _ in range(20):
        poll = auth_client.get(f"/api/jobs/{job_id}")
        assert poll.status_code == 200
        status = poll.get_json()
        if status["status"] in {"completed", "failed"}:
            break
        time.sleep(0.05)

    assert status is not None
    assert status["status"] == "failed"
    assert status["exit_code"] == 1
    assert "login" in (status.get("error") or "").lower()


def test_concurrent_job_rejected(auth_client, monkeypatch):
    import backend.jobs as jobs

    monkeypatch.setattr(
        "backend.jobs.subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(
            args=[], returncode=0, stdout="", stderr=""
        ),
    )
    # Do not run the worker — leave the slot occupied.
    monkeypatch.setattr(
        "backend.jobs.threading.Thread",
        lambda *a, **k: type("T", (), {"start": lambda self: None})(),
    )

    first = auth_client.post(
        "/api/jobs",
        json={
            "source": "irvine-news",
            "settings": {"max_articles": 1, "outlets": ["irvine-standard"]},
        },
    )
    assert first.status_code == 202
    assert jobs._running_job_id is not None

    second = auth_client.post(
        "/api/jobs",
        json={
            "source": "irvine-news",
            "settings": {"max_articles": 1, "outlets": ["irvine-standard"]},
        },
    )
    assert second.status_code == 409

    with jobs._job_lock:
        jobs._running_job_id = None
