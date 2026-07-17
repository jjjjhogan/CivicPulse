# Backend platform handoff

**Branch:** `feature/backend-platform` (cut from `main` after `chore/backend-polish`)

## Goal

Real auth, SQLite + ORM, scrape job API, migrate signals off JSON-only storage.

## Status (implemented on this branch)

- Package: `backend/` (models, auth, jobs, routes); entry `scripts/dashboard_server.py`
- SQLite models: `User`, `Signal`, `ScrapeJob` — import via `python scripts/import_signals.py`
- `/api/auth` signup/login/logout/me (session cookie + hashed passwords)
- `/api/jobs` POST/GET wrapping existing scrapers; legacy `/api/scrape/*` kept (auth-gated)
- UI: `login.js` + dashboard gate/logout + scrapers panel → job endpoints

## Do not do on this branch

NLP / classifier upgrades, analytics redesign, caption experiments → `feature/signal-intelligence` later.
