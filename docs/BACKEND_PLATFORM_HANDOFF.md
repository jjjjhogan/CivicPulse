# Backend platform handoff

**Branch:** `feature/backend-platform` (cut from `main` after `chore/backend-polish`)

## Goal

Real auth, SQLite + ORM, scrape job API, migrate signals off JSON-only storage.

## Current state

- Flask app: `scripts/dashboard_server.py`
- Scrapers: `POST /api/scrape/<source>` (tiktok, irvine-news, reddit, twitter)
- Signals: `data/signals/{tiktok,reddit,twitter,news}.json` + `feed.json`
- Login UI: `login.js` is **localStorage demo only** — no `/api/auth`
- Config: `.env.example` (`FLASK_SECRET_KEY`, `HOST`, `PORT`) + dotenv in server

## Do not do on this branch

NLP / classifier upgrades, analytics redesign, caption experiments → `feature/signal-intelligence` later.

## First tasks (in order)

1. **DB models + import** — SQLite + SQLAlchemy (or similar): `User`, `Signal`, `ScrapeJob`; script/command to import existing `data/signals/*.json`
2. **`/api/auth`** — signup / login / logout with hashed passwords + session cookie; replace `login.js` localStorage accounts
3. **`/api/jobs`** — `POST /api/jobs` `{source, settings}` → job id; `GET /api/jobs/<id>` status/log; wrap existing scrape scripts (keep local subprocess for now)
4. **Wire UI** — `login.js` → real API; `dashboard.js` scraper panel → job endpoints; gate dashboard/scrape if not logged in

## Suggested layout

Introduce a small package (e.g. `backend/` or `civicpulse/`) instead of only growing `scripts/dashboard_server.py`; still serve static UI + APIs from one Flask app for now.

## Key files

- `scripts/dashboard_server.py`, `scrapers/schema.py`, `scrapers/feed.py`
- `login.js`, `dashboard.js`, `requirements.txt`, `.env.example`
- Scrape entrypoints: `scripts/scrape_tiktok.py`, `scripts/scrape_news.py`, `scripts/process_reddit_scrape.py`, `scripts/process_twitter_scrape.py`
