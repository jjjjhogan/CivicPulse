Repo: CivicPulse (Ryan/). Roadmap: Weeks 1–2 — platform harden: SQLite as source of truth, API/runbook, TikTok Chrome fixes.

Context: backend/ already has User/Signal/ScrapeJob, /api/auth, /api/jobs, import_signals, pytest. Dashboard still mixes JSON/localStorage in places. TikTok Selenium is flaky (login wall, comment panel, Chrome profile).

Goal: Local demo from cold start in <10 minutes; DB-backed signals are the truth; TikTok scrape is more reliable on a desktop (not cloud).

Work in order:
1. Runbook: README (or docs/) — pip install → import_signals → reprocess_signals → dashboard_server; note auth + pytest -q.
2. SQLite as source of truth: ensure GET /api/signals (and feed) prefer DB after import; sync after jobs already exists — fix gaps so dashboard.js/signals-data.js don’t silently depend on stale JSON when DB has rows. Add/adjust API only if needed for reports/votes; keep schema changes minimal.
3. Tests: keep pytest -q green; add/extend tests for any new API behavior.
4. TikTok Selenium (scrapers/tiktok/): persistent Chrome user-data-dir / profile so a one-time manual login sticks; document login-wall behavior; harden comment-panel open/dismiss. Do NOT try to run TikTok headless on a server.
5. Jobs API clarity: if Chrome isn’t available or TikTok fails login wall, job error/log should say so clearly.

Out of scope: Postgres, Render, Firebase, major UI redesign, new mayor features (resolution status, briefing), classifier architecture rewrites (label tweaks OK if needed for a scrape fix).

Done when: import → server → /api/signals from DB; pytest green; TikTok docs + profile path work on this PC; news/import jobs unchanged and healthy.
Branch suggestion: feature/platform-harden-w1-2
