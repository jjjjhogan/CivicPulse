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
data/signals/                         # normalized CivicSignal JSON (also imported to SQLite)
docs/INTEGRATION.md                   # API + signal contract
.env.example                          # HOST / PORT / FLASK_SECRET_KEY / DATABASE_URL
```

Note: root `main.py` is a legacy UCLA Selenium prototype, unrelated to CivicPulse ingestion.

## Quick start

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
copy .env.example .env         # optional

python scripts/import_signals.py
python scripts/dashboard_server.py
```

Open http://127.0.0.1:8080/login.html, create an account, then use the dashboard Scrapers panel.

See [docs/INTEGRATION.md](docs/INTEGRATION.md) for endpoints, CLI examples, and the signal contract.
