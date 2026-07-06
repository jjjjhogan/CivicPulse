# CivicPulse

CivicPulse is an AI civic-sentiment research platform for city leadership — ingesting resident voices from social media, classifying issues (potholes, noise, sanitation, public safety, housing), and surfacing geographic clusters on a map.

## Repository layout

```
index.html / script.js / styles.css   # landing page (on main)
scrapers/
  categories.py                       # shared issue taxonomy
  schema.py                           # CivicSignal output contract
  tiktok/                             # TikTok Selenium scraper (this branch)
scripts/scrape_tiktok.py             # TikTok CLI
data/
  raw/                                # full scrape payloads
  signals/                            # normalized output for the UI
docs/INTEGRATION.md                   # merge guide for main
```

## TikTok scraper

```bash
pip install -r requirements.txt

python scripts/scrape_tiktok.py \
  --tag-url "https://www.tiktok.com/tag/irvine" \
  --tag-url "https://www.tiktok.com/tag/newportbeach" \
  --max-videos 3 \
  --max-comments 10
```

Outputs:
- `data/raw/tiktok_scrape.json` — full scrape data
- `data/signals/feed.json` — landing-page-ready signal cards

## Dashboard

Run the local server to use the Irvine civic dashboard with live TikTok ingestion:

```bash
pip install -r requirements.txt
python scripts/dashboard_server.py
```

Open http://127.0.0.1:8080/dashboard.html — the Scrapers panel runs `scripts/scrape_tiktok.py` and loads results from `data/signals/tiktok.json`.

See [docs/INTEGRATION.md](docs/INTEGRATION.md) for the full signal contract and merge notes.
