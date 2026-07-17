"""Shared paths and scrape defaults for the CivicPulse backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SIGNALS_DIR = ROOT / "data" / "signals"
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "civicpulse.db"

SCRAPE_TIKTOK = ROOT / "scripts" / "scrape_tiktok.py"
SCRAPE_NEWS = ROOT / "scripts" / "scrape_news.py"
PROCESS_REDDIT = ROOT / "scripts" / "process_reddit_scrape.py"
PROCESS_TWITTER = ROOT / "scripts" / "process_twitter_scrape.py"

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

NEWS_DEFAULTS = {
    "outlets": ["irvine-standard", "irvine-weekly", "voice-of-oc"],
    "max_articles": 50,
    "require_category_match": True,
}


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        return f"sqlite:///{DB_PATH.as_posix()}"
    prefix = "sqlite:///"
    if url.startswith(prefix) and not url.startswith("sqlite:////"):
        rel = url[len(prefix) :]
        if rel and not Path(rel).is_absolute():
            return f"sqlite:///{(ROOT / rel).as_posix()}"
    return url
