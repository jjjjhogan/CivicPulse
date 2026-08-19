# CivicPulse — session plan (Sessions 25–26: Research summary + print)

**Goal:** Add a summary API + print-ready HTML page so a research topic produces a one-pager briefing for the mayor.

---

## Sessions 25–26 — Research summary API + print/HTML

### Completed

**Backend API (`routes/research.py`):**
- [x] `GET /api/researches/<id>/summary` — structured summary with hit stats, category/source breakdown, date range, top 10 signals, linked jobs
- [x] Returns aggregated `by_category`, `by_source`, `date_range`, `top_signals`, `jobs`

**Print page (`research-summary.html`):**
- [x] Standalone page fetches summary API and renders clean one-pager
- [x] Header: brand, title, topic, status, signal count, date range, created date
- [x] Category/keyword tags
- [x] Stats grid with total + per-category signal counts
- [x] Top 10 signals with title, body excerpt, source, categories, date
- [x] Data collection jobs table (source, status, date)
- [x] Notes section
- [x] Footer with generated date
- [x] Print/Save PDF button + back-to-workspace link
- [x] `@media print` hides toolbar

**Frontend (`research-detail.js`):**
- [x] Summary tab added (third tab alongside Archive and Jobs)
- [x] Inline summary preview: stat cards, date range, top 5 signals
- [x] "Print Summary" button opens `research-summary.html` in new tab
- [x] Summary loads lazily on first tab click, cached after

**CSS (`research.css`):**
- [x] `.summary-stats`, `.summary-stat` — stat card layout
- [x] `.summary-date-range` — date range text
- [x] `.summary-section-label` — section headers
- [x] `.summary-signal`, `.summary-signal-title`, `.summary-signal-meta` — signal list

**Bug fixes (pre-existing):**
- [x] Fixed `_create_and_start_job` missing `research_id` parameter
- [x] Fixed `selenium_available` missing from `routes/jobs.py` import
- [x] Fixed `test_concurrent_job_rejected` empty stub causing IndentationError
- [x] Fixed job tests using `auth_client` instead of `dev_client` (scrapers_allowed guard)

**Tests (`test_research_api.py`):**
- [x] `test_research_summary` — summary endpoint returns structured data
- [x] `test_research_summary_not_found` — 404 for missing research
- [x] All 151 tests pass

### Modified files

| File | Change |
|------|--------|
| `backend/routes/research.py` | `GET /api/researches/<id>/summary` endpoint |
| `backend/routes/jobs.py` | Fixed `research_id` param + `selenium_available` import |
| `research-summary.html` | New — print-ready summary page |
| `research-detail.js` | Summary tab + inline preview + Print button |
| `research.css` | Summary preview styles |
| `tests/test_research_api.py` | 2 new summary tests + fixed `dev_client` fixture usage |
| `tests/test_jobs_api.py` | Fixed empty stub + `dev_client` fixture usage |

### Browser verification

- [x] Summary tab appears in workspace (Archive / Jobs / Summary)
- [x] Clicking Summary tab loads inline preview with stat cards + top signals
- [x] Print Summary button links to `research-summary.html?id=...`
- [x] Print page renders: header, stats grid, top signals, footer
- [x] Print page back link returns to workspace
- [x] No console errors

---

## Exit criteria

- [x] Summary API returns structured aggregation of research data
- [x] Print page renders one-pager with stats, signals, jobs, notes
- [x] Summary tab in workspace shows inline preview
- [x] Print/Save PDF button works
- [x] 151 tests pass
- [x] Browser verification

---

## Previous sessions

- **Sessions 23–24** — TikTok/desktop job link + operator copy
- **Sessions 21–22** — Research-scoped jobs (research_id FK, post-job matching, Jobs tab)
- **Sessions 19–20** — Topic keyword assist + category picker
- **Sessions 17–18** — Research workspace UI (PATCH/DELETE, tabs, inline edit, filters)
- **Session 16** — GitHub Actions CI workflow
- **Session 15** — Desktop-only Selenium messaging
- **Session 14** — Render deployment config
- **Session 13** — Cold demo end-to-end on Firestore

---

## Next: Sessions 27–28 — Map filter by research + Phase D confidence polish

Per [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md): Map filter pins by active research; Phase D confidence/method UX polish if demos still confuse.
