"""
CivicPulse dashboard server — serves the static UI and runs ingestion scrapers.

Usage:
    python scripts/dashboard_server.py
    python scripts/dashboard_server.py --port 8080
"""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, request, send_from_directory

ROOT = Path(__file__).resolve().parent.parent
SIGNALS_DIR = ROOT / "data" / "signals"
SCRAPE_SCRIPT = ROOT / "scripts" / "scrape_tiktok.py"

sys.path.insert(0, str(ROOT))
from scrapers.categories import CivicIssueCategory  # noqa: E402

app = Flask(__name__)

_scrape_lock = threading.Lock()
_scrape_state: dict = {
    "status": "idle",
    "source": None,
    "started_at": None,
    "finished_at": None,
    "exit_code": None,
    "command": None,
    "log": "",
    "error": None,
}

TIKTOK_DEFAULTS = {
    "mode": "tags",
    "tag_urls": [
        "https://www.tiktok.com/tag/irvine",
        "https://www.tiktok.com/tag/newportbeach",
    ],
    "max_videos": 10,
    "max_comments": 25,
    "headless": False,
    "include_all_comments": False,
}


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _build_scrape_command(payload: dict) -> list[str]:
    mode = payload.get("mode", "tags")
    cmd = [sys.executable, str(SCRAPE_SCRIPT)]

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

    max_videos = int(payload.get("max_videos", 3))
    max_comments = int(payload.get("max_comments", 25))
    cmd.extend(["--max-videos", str(max_videos)])
    cmd.extend(["--max-comments", str(max_comments)])

    if payload.get("headless", False):
        cmd.append("--headless")
    if payload.get("include_all_comments"):
        cmd.append("--include-all-comments")

    return cmd


def _run_scrape(cmd: list[str], *, source: str) -> None:
    global _scrape_state
    with _scrape_lock:
        _scrape_state = {
            "status": "running",
            "source": source,
            "started_at": time.time(),
            "finished_at": None,
            "exit_code": None,
            "command": " ".join(cmd),
            "log": "",
            "error": None,
        }

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
        with _scrape_lock:
            _scrape_state["status"] = "completed" if result.returncode == 0 else "failed"
            _scrape_state["exit_code"] = result.returncode
            _scrape_state["finished_at"] = time.time()
            _scrape_state["log"] = log
            if result.returncode != 0:
                _scrape_state["error"] = f"Scraper exited with code {result.returncode}"
    except Exception as exc:  # noqa: BLE001
        with _scrape_lock:
            _scrape_state["status"] = "failed"
            _scrape_state["finished_at"] = time.time()
            _scrape_state["error"] = str(exc)


def _start_scrape(payload: dict, *, source: str):
    with _scrape_lock:
        if _scrape_state["status"] == "running":
            return jsonify({"error": "A scrape is already running."}), 409

    try:
        cmd = _build_scrape_command(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    thread = threading.Thread(target=_run_scrape, args=(cmd,), kwargs={"source": source}, daemon=True)
    thread.start()
    return jsonify({"status": "started", "command": " ".join(cmd)}), 202


@app.get("/api/signals")
def api_signals():
    tiktok = _read_json(SIGNALS_DIR / "tiktok.json", [])
    reddit = _read_json(SIGNALS_DIR / "reddit.json", [])
    twitter = _read_json(SIGNALS_DIR / "twitter.json", [])
    signals = tiktok + reddit + twitter
    return jsonify({"count": len(signals), "signals": signals})


@app.get("/api/signals/feed")
def api_feed():
    feed = _read_json(SIGNALS_DIR / "feed.json", [])
    return jsonify({"count": len(feed), "signals": feed})


@app.get("/api/manifest")
def api_manifest():
    manifest = _read_json(SIGNALS_DIR / "manifest.json", None)
    return jsonify({"manifest": manifest})


@app.get("/api/config")
def api_config():
    return jsonify(
        {
            "categories": [c.value for c in CivicIssueCategory],
            "tiktok_defaults": TIKTOK_DEFAULTS,
        }
    )


@app.get("/api/scrape/status")
def api_scrape_status():
    with _scrape_lock:
        return jsonify(dict(_scrape_state))


@app.post("/api/scrape/<source>")
def api_scrape_source(source: str):
    if source == "tiktok":
        payload = request.get_json(silent=True) or dict(TIKTOK_DEFAULTS)
        merged = {**TIKTOK_DEFAULTS, **payload}
        return _start_scrape(merged, source="tiktok")
    return jsonify({"error": f"Scraper '{source}' is not implemented yet."}), 501


@app.get("/dashboard")
def dashboard_shortcut():
    return redirect("/dashboard.html")


@app.route("/", defaults={"filename": "index.html"})
@app.route("/<path:filename>")
def static_files(filename: str):
    if filename.startswith("api/"):
        abort(404)
    path = ROOT / filename
    if not path.is_file():
        abort(404)
    return send_from_directory(ROOT, filename)


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CivicPulse dashboard server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if _port_in_use(args.host, args.port):
        print(
            f"Port {args.port} is already in use on {args.host}. "
            "Stop the other process first, or run with --port 8081."
        )
        raise SystemExit(1)

    base = f"http://{args.host}:{args.port}"
    print(f"CivicPulse server running:")
    print(f"  Dashboard: {base}/dashboard.html")
    print(f"  Landing:   {base}/")
    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)


if __name__ == "__main__":
    main()
