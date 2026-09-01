"""Shared paths and scrape defaults for the CivicPulse backend."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

SIGNALS_DIR = ROOT / "data" / "signals"
POOL_DIR = ROOT / "data" / "pool"
RAW_DIR = ROOT / "data" / "raw"
BACKUP_DIR = ROOT / "data" / "backups"
DB_PATH = ROOT / "data" / "civicpulse.db"

SCRAPE_TIKTOK = ROOT / "scripts" / "scrape_tiktok.py"
SCRAPE_NEWS = ROOT / "scripts" / "scrape_news.py"
PROCESS_REDDIT = ROOT / "scripts" / "process_reddit_scrape.py"
PROCESS_TWITTER = ROOT / "scripts" / "process_twitter_scrape.py"

# Curated Irvine / Orange County, CA tag pages for the scraper UI.
# Avoid ambiguous tags like #orangecountynews (FL) and #irvinenews (UK).
TIKTOK_TAG_OPTIONS = [
    {
        "id": "irvine",
        "label": "#irvine",
        "group": "location",
        "default": True,
    },
    {
        "id": "irvinecalifornia",
        "label": "#irvinecalifornia",
        "group": "location",
        "default": False,
    },
    {
        "id": "ucirvine",
        "label": "#ucirvine",
        "group": "location",
        "default": False,
    },
    {
        "id": "newportbeach",
        "label": "#newportbeach",
        "group": "location",
        "default": True,
    },
    {
        "id": "orangecounty",
        "label": "#orangecounty",
        "group": "location",
        "default": False,
        "hint": "Some FL noise possible — skip #orangecountynews",
    },
    {
        "id": "ocrundown",
        "label": "#ocrundown",
        "group": "news",
        "default": False,
    },
    {
        "id": "foxla",
        "label": "#foxla",
        "group": "news",
        "default": False,
    },
    {
        "id": "cbsla",
        "label": "#cbsla",
        "group": "news",
        "default": False,
    },
    {
        "id": "ktla",
        "label": "#ktla",
        "group": "news",
        "default": False,
    },
]

TIKTOK_DEFAULTS = {
    "mode": "tags",
    "tag_urls": [
        f"https://www.tiktok.com/tag/{tag['id']}"
        for tag in TIKTOK_TAG_OPTIONS
        if tag.get("default")
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


DATA_BACKEND = os.environ.get("DATA_BACKEND", "sqlite")


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
