# CivicPulse

CivicPulse is an AI civic-sentiment research platform for city leadership — ingesting resident voices from social media, classifying issues (potholes, noise, sanitation, public safety, housing, immigration), and surfacing geographic clusters on a map.

## Repository layout

```
index.html / script.js / styles.css   # landing page
dashboard.html / dashboard.js         # Irvine civic dashboard (auth-gated)
login.html / login.js                 # signup / login → /api/auth
backend/                              # Flask app, SQLAlchemy models, jobs
scrapers/                             # categories, schema, tiktok/news/reddit/twitter
scripts/                              # dashboard_server, import_signals, scrape/process CLIs
data/raw/                             # scrape / import payloads
data/signals/                         # normalized CivicSignal JSON (imported into SQLite)
docs/INTEGRATION.md                   # API + signal contract
docs/TIKTOK_SCRAPE.md                 # Chrome profile + login-wall notes
.env.example                          # HOST / PORT / FLASK_SECRET_KEY / DATABASE_URL
```

Note: root `main.py` is a legacy UCLA Selenium prototype, unrelated to CivicPulse ingestion.

## Local demo (cold start, ~10 minutes)

SQLite is the source of truth for the dashboard. JSON under `data/signals/` is the ingest/export format; load it into the DB before serving.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
# source .venv/bin/activate    # macOS / Linux
pip install -r requirements.txt
copy .env.example .env         # optional (Windows); or: cp .env.example .env

python scripts/import_signals.py
python scripts/reprocess_signals.py   # refresh classification metadata on JSON, then re-sync DB
python scripts/dashboard_server.py
```

Open http://127.0.0.1:8080/login.html, **create an account** (session cookie auth), then open the dashboard. Scrapers panel calls `/api/jobs` (auth required).

Verify DB-backed signals: http://127.0.0.1:8080/api/signals — response includes `"storage": "db"` after import.

| Step | Purpose |
|------|---------|
| `import_signals.py` | Load `data/signals/*.json` → SQLite (`data/civicpulse.db`) |
| `reprocess_signals.py` | Reclassify JSON, rebuild feed, sync rows back into SQLite |
| `dashboard_server.py` | Flask app: auth, signals, scrape jobs |

Useful flags:

```bash
python scripts/import_signals.py --replace   # wipe Signal table, then import
```

## Testing

```bash
pytest -q
```

Covers auth, SQLite signal import, mocked scrape jobs, and classifier/reprocess helpers (no Selenium).

## TikTok scrape (desktop only)

See [docs/TIKTOK_SCRAPE.md](docs/TIKTOK_SCRAPE.md). Default is **anonymous / no-login** headed Chrome (persistent profile under `data/chrome/tiktok_profile/` only stores cookies/dismissals). Log in only if comments stay blocked.

## More detail

See [docs/INTEGRATION.md](docs/INTEGRATION.md) for endpoints, CLI scrape examples, and the signal contract.
