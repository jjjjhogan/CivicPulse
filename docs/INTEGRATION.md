# Integration guide: scraping-tiktok -> main

This branch is structured to merge cleanly with `main`, which already contains the CivicPulse landing page (`index.html`, `script.js`, `styles.css`).

## What is on main today

- Prototype landing page with hardcoded `SAMPLE_SIGNALS` in `script.js`
- Legacy `main.py` UCLA prototype (unrelated to CivicPulse ingestion)

## What this branch adds

```
scrapers/
  categories.py      # shared issue categories + classify()
  schema.py          # CivicSignal output contract
  tiktok/            # Selenium TikTok scraper
scripts/
  scrape_tiktok.py   # CLI entry point
data/
  raw/               # full scrape payloads
  signals/           # normalized output for the UI
```

## Shared signal contract

The landing page expects records shaped like:

```json
{
  "outlet": "TikTok #irvine",
  "title": "Pothole on Culver and Alton has been there for a month now",
  "categories": ["potholes"],
  "published_utc": "2026-07-06"
}
```

TikTok scraping writes two files after each run:

| File | Purpose |
|------|---------|
| `data/raw/tiktok_scrape.json` | Full scrape payload (videos, comments, metadata) |
| `data/signals/tiktok.json` | Normalized `CivicSignal` records with full fields |
| `data/signals/feed.json` | Landing-page-compatible array for `script.js` |
| `data/signals/manifest.json` | Lists which sources have been ingested |

## Run TikTok ingestion

```bash
pip install -r requirements.txt

python scripts/scrape_tiktok.py \
  --tag-url "https://www.tiktok.com/tag/irvine" \
  --tag-url "https://www.tiktok.com/tag/newportbeach" \
  --max-videos 3 \
  --max-comments 10
```

By default only comments matching a civic category are exported. Use `--include-all-comments` to export everything.

## Wiring the landing page

On `main`, replace `SAMPLE_SIGNALS` in `script.js` with a fetch to the generated feed:

```js
fetch("data/signals/feed.json")
  .then((res) => res.json())
  .then(renderSignals)
  .catch(() => renderSignals(SAMPLE_SIGNALS));
```

For local development, serve the repo root with any static file server so the browser can load the JSON file.

## Merge notes

- No changes required to `index.html` / `styles.css` for the first integration
- `main.py` on main is legacy; leave it or remove in a separate cleanup PR
- Other ingestion sources (Reddit, news) are not on main yet — when added, they should write to `data/signals/<source>.json` using the same `CivicSignal` schema and merge into `feed.json`
- Shared classification lives in `scrapers/categories.py` so all sources use the same issue taxonomy

## Suggested merge order

1. Merge `scraping-tiktok` into `main`
2. Coworker wires `script.js` to read `data/signals/feed.json`
3. Add future scrapers under `scrapers/<source>/` using the same export pattern
