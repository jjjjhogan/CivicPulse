# Integration guide: scrapers, signals, and dashboard API

CivicPulse ingests resident signals from social/news sources, normalizes them to `CivicSignal`, and serves them through the dashboard.

## Repository pieces

```
scrapers/
  categories.py      # shared issue categories + classify()
  schema.py          # CivicSignal output contract
  feed.py            # rebuild data/signals/feed.json
  tiktok/            # Selenium TikTok scraper
  news/              # Irvine RSS news scraper
  reddit/            # Reddit JSON → signals
  twitter/           # Twitter JSON → signals
scripts/
  dashboard_server.py
  scrape_tiktok.py
  scrape_news.py
  process_reddit_scrape.py
  process_twitter_scrape.py
data/
  raw/               # full scrape / import payloads
  signals/           # normalized output for the UI
```

Legacy note: root `main.py` is an unrelated UCLA Selenium prototype — not part of CivicPulse ingestion. Prefer leaving it alone or removing it in a dedicated cleanup PR.

## Shared signal contract

Full records (`data/signals/<source>.json`) follow `scrapers/schema.py`:

```json
{
  "source": "tiktok",
  "outlet": "TikTok #irvine",
  "title": "Pothole on Culver and Alton has been there for a month now",
  "body": "...",
  "url": "https://...",
  "categories": ["potholes"],
  "published_utc": "2026-07-06",
  "metadata": {}
}
```

Landing feed (`data/signals/feed.json`) uses the slim card shape (`outlet`, `title`, `categories`, `published_utc`).

| File | Purpose |
|------|---------|
| `data/raw/<source>_scrape.json` | Raw scrape or import payload |
| `data/signals/tiktok.json` | Normalized TikTok signals |
| `data/signals/news.json` | Normalized news signals |
| `data/signals/reddit.json` | Normalized Reddit signals |
| `data/signals/twitter.json` | Normalized Twitter signals |
| `data/signals/feed.json` | Merged landing-page feed |
| `data/signals/manifest.json` | Ingest metadata |

## Run ingestion (CLI)

```bash
pip install -r requirements.txt
# optional: copy .env.example → .env

python scripts/scrape_tiktok.py \
  --tag-url "https://www.tiktok.com/tag/irvine" \
  --max-videos 3 --max-comments 10

python scripts/scrape_news.py --outlet irvine-standard --max-articles 20

python scripts/process_reddit_scrape.py --input data/raw/reddit_scrape.json
python scripts/process_twitter_scrape.py --input data/raw/twitter_scrape.json
```

## Dashboard server (local demo)

Cold start (SQLite is the dashboard source of truth):

```bash
pip install -r requirements.txt
python scripts/import_signals.py
python scripts/reprocess_signals.py   # updates JSON + re-syncs SQLite
python scripts/dashboard_server.py
# HOST / PORT / FLASK_SECRET_KEY / DATABASE_URL from .env; CLI --host/--port override
```

```bash
python scripts/import_signals.py --replace   # wipe Signal table first
pytest -q                                    # auth, import, mocked jobs (no Selenium)
```

Open http://127.0.0.1:8080/login.html — create an account (session cookie), then use the dashboard Scrapers panel.

| Endpoint | Purpose |
|----------|---------|
| `POST /api/auth/signup` | Create account (hashed password + session cookie) |
| `POST /api/auth/login` | Log in |
| `POST /api/auth/logout` | Log out |
| `GET /api/auth/me` | Current session user |
| `GET /api/signals` | Signals from SQLite when present (`storage: "db"`); else JSON fallback (`storage: "json"`). Includes `source: "resident"` reports. |
| `GET /api/signals/feed` | Landing-page feed shape (same DB-first rule) |
| `POST /api/reports` | Create resident report → SQLite `Signal` (`source: resident`) |
| `GET /api/reports` | List resident signals only |
| `GET /api/votes` | Vote tallies for resident reports (`mine` when logged in) |
| `POST /api/votes` | Toggle up/down vote `{signal_id, choice}` (auth required) |
| `GET /api/config` | Categories, TikTok/news defaults, news outlets |
| `POST /api/jobs` | Start scrape job `{source, settings}` → `{id, status}` (auth required) |
| `GET /api/jobs/<id>` | Job status + log (auth required); TikTok/Chrome failures include readable `error` text |
| `POST /api/scrape/<source>` | Legacy scrape API (auth required; creates a job) |
| `GET /api/scrape/status` | Legacy status poll (auth required) |

Package layout: `backend/` (models, auth, jobs, routes). Entry point remains `scripts/dashboard_server.py`.

TikTok desktop Chrome profile + login-wall notes: [TIKTOK_SCRAPE.md](TIKTOK_SCRAPE.md).

## Wiring the landing page

When the Flask server is running, prefer the API (DB-backed after import):

```js
fetch("/api/signals/feed")
  .then((res) => res.json())
  .then((data) => renderSignals(data.signals || []))
  .catch(() => renderSignals(SAMPLE_SIGNALS));
```

Static fallback without the server: `data/signals/feed.json`.

## Source conventions

New scrapers should live under `scrapers/<source>/`, write `data/signals/<source>.json` using `CivicSignal`, and rebuild `feed.json` via `scrapers/feed.py`. Classification stays in `scrapers/categories.py`. Completed scrape jobs re-sync JSON into SQLite automatically.
