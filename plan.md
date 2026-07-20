Repo: CivicPulse (Ryan/). Roadmap: Weeks 1–2 — UI / product polish only.

Context: Pre-alpha mayor dashboard. Backend auth + /api/signals + /api/jobs already exist. Do NOT migrate to Postgres/Render/Firebase. Do NOT rewrite scrapers or the classifier.

Goal: Demo feels trustworthy — empty states, clearer scrape feedback, confidence on cards, less localStorage-only UX where easy.

Work in order:
1. Login + dashboard: empty/loading/error states; scrape job failures show readable messages (use job log/error from /api/jobs/<id>); confirm logged-out redirect still works.
2. Signal cards / feed / source analytics (dashboard.js, source.js, signals-data.js): surface metadata.classification.confidence (and method if useful) without cluttering the UI.
3. Resident reports (report.js): keep UX polish; if you wire persistence, prefer calling existing APIs — do not invent a new backend. localStorage OK as interim if no API exists yet.
4. Visual/UX cleanup only within the existing design language (styles.css, dashboard.css, login.css) — no full redesign, no new product modules (briefing, resolution status).

Out of scope: Selenium, SQLite schema changes, new API routes (unless a tiny read-only helper is required and you coordinate), NLP/label edits, Render/deploy.

Done when: cold open → login → dashboard shows signals with confidence; failed scrape is understandable; pytest still green if you touch shared code.
Branch suggestion: feature/ui-polish-w1-2