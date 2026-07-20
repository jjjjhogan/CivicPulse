# Backend platform handoff

**Branch:** `feature/backend-platform` (merged); follow-up harden on `feature/platform-harden-w1-2`

## Goal

Real auth, SQLite + ORM, scrape job API, migrate signals off JSON-only storage.

## Status

- Package: `backend/` (models, auth, jobs, routes); entry `scripts/dashboard_server.py`
- SQLite models: `User`, `Signal`, `ScrapeJob` — import via `python scripts/import_signals.py`
- `/api/auth` signup/login/logout/me (session cookie + hashed passwords)
- `/api/jobs` POST/GET wrapping existing scrapers; legacy `/api/scrape/*` kept (auth-gated)
- `/api/signals` + `/api/signals/feed` prefer SQLite (`storage: "db"`); JSON only when table empty
- UI: `login.js` + dashboard gate/logout + scrapers panel → job endpoints
- TikTok: persistent Chrome profile + login-wall errors — see `docs/TIKTOK_SCRAPE.md`
- Local demo runbook: root `README.md`

## Do not do on this branch

NLP / classifier upgrades, analytics redesign, caption experiments → `feature/signal-intelligence` later.
Postgres / Render / Firebase — out of scope for W1–2 harden.
