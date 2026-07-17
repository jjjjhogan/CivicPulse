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

## Dashboard server

```bash
python scripts/dashboard_server.py
# or: HOST / PORT / FLASK_SECRET_KEY from .env; CLI --host/--port override
```

Open http://127.0.0.1:8080/dashboard.html — Scrapers panel configures and runs sources.

| Endpoint | Purpose |
|----------|---------|
| `GET /api/signals` | Concatenated signals from tiktok + reddit + twitter + news |
| `GET /api/signals/feed` | Landing-page `feed.json` |
| `GET /api/config` | Categories, TikTok/news defaults, news outlets |
| `POST /api/scrape/tiktok` | Run TikTok scraper (JSON body: tags, max_videos, max_comments, …) |
| `POST /api/scrape/irvine-news` | Run news RSS scraper (outlets, max_articles, require_category_match) |
| `POST /api/scrape/reddit` | Import Reddit scrape JSON (paste body or upload file) → process |
| `POST /api/scrape/twitter` | Import Twitter scrape JSON → process |
| `GET /api/scrape/status` | Poll scrape progress and logs (one job at a time; `409` if busy) |

Auth is still client-side demo login (`login.js` localStorage). Real auth / DB / job IDs belong on `feature/backend-platform`.

## Wiring the landing page

```js
fetch("data/signals/feed.json")
  .then((res) => res.json())
  .then(renderSignals)
  .catch(() => renderSignals(SAMPLE_SIGNALS));
```

Or use `GET /api/signals/feed` when the Flask server is running.

## Source conventions

New scrapers should live under `scrapers/<source>/`, write `data/signals/<source>.json` using `CivicSignal`, and rebuild `feed.json` via `scrapers/feed.py`. Classification stays in `scrapers/categories.py`.
