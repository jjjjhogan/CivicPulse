# CivicPulse — session plan (Sessions 21–22: Research-scoped jobs)

**Goal:** Wire scrape jobs to research topics so the Jobs tab fills after a news job, and new signals auto-match into the research.

---

## Sessions 21–22 — Research-scoped jobs

### Completed

**Backend model + migration:**
- [x] Added `research_id` FK to `ScrapeJob` model (nullable, ON DELETE SET NULL)
- [x] `to_dict()` includes `research_id` in job responses
- [x] Schema migration v2: `ALTER TABLE scrape_jobs ADD COLUMN research_id`

**Store protocol + implementations:**
- [x] `JobStore.create_job` accepts optional `research_id`
- [x] `JobStore.list_jobs_for_research(research_id)` — query jobs linked to a research
- [x] `ResearchStore.add_hits` — incremental hit addition (skips duplicates)
- [x] All four store implementations updated (SQLite, Firestore, standalone)

**Post-job matching hook:**
- [x] `_match_research_after_job` in `backend/jobs.py` — after job completes + signals sync, auto-matches all signals against the linked research using shared `match_signals()` function
- [x] Extracted `_match_signals` from `routes/research.py` into shared `backend/research_match.py`

**API:**
- [x] `POST /api/jobs` accepts optional `research_id` to link a job to a research
- [x] `GET /api/researches/<id>/jobs` — list jobs linked to a research

**Frontend (`research-detail.js`):**
- [x] Jobs tab (renamed from "New") shows linked job cards with source, status, time
- [x] Source selector (irvine-news, tiktok if available) + "Start Job" button
- [x] Job cards show color-coded status badges (completed/running/failed/pending)
- [x] Tab count badge shows number of linked jobs
- [x] Fetches jobs in parallel with research data on page load

**CSS (`research.css`):**
- [x] `.jobs-list`, `.job-card`, `.job-card-top` — job card layout
- [x] `.job-source`, `.job-status`, `.job-time`, `.job-error` — job card elements
- [x] Status-specific colors: completed (green), running (blue), failed (red)

**Tests:**
- [x] `test_list_research_jobs_empty` — GET returns empty jobs array
- [x] `test_list_research_jobs_not_found` — 404 for missing research
- [x] `test_create_job_with_research_id` — job creation with research_id, verify linkage
- [x] All 139 tests pass

### Modified files

| File | Change |
|------|--------|
| `backend/models.py` | Added `research_id` FK to ScrapeJob |
| `backend/migrate.py` | v2 migration for research_id column |
| `backend/store.py` | Updated JobStore + ResearchStore protocols, standalone store |
| `backend/store_sqlite.py` | `research_id` in create_job, `list_jobs_for_research`, `add_hits` |
| `backend/store_firestore.py` | Same updates for Firestore |
| `backend/research_match.py` | New — shared `match_signals()` extracted from routes |
| `backend/jobs.py` | `_match_research_after_job` post-completion hook |
| `backend/routes/jobs.py` | Accept `research_id` in job creation |
| `backend/routes/research.py` | Uses shared matcher, `GET /api/researches/<id>/jobs` |
| `research-detail.js` | Jobs tab with cards, source picker, Start Job button |
| `research.css` | Job card styles |
| `tests/test_research_api.py` | 3 new tests for research-job linking |

### Browser verification

- [x] Jobs tab shows "Jobs 0" initially (no linked jobs)
- [x] Source selector shows irvine-news + tiktok options
- [x] After starting a news job: job card appears with "irvine-news" + "completed" status
- [x] Archive hit count increased (142 → 146) after job ran, confirming auto-match hook
- [x] No console errors

---

## Exit criteria

- [x] `research_id` FK on ScrapeJob with migration
- [x] Job creation API accepts `research_id`
- [x] Post-job hook auto-matches signals against linked research
- [x] Research jobs endpoint lists linked jobs
- [x] Jobs tab in workspace shows cards + Start Job button
- [x] 139 tests pass
- [x] Browser verification — full flow working

---

## Previous sessions

- **Sessions 19–20** — Topic keyword assist + category picker
- **Sessions 17–18** — Research workspace UI (PATCH/DELETE, tabs, inline edit, filters)
- **Session 16** — GitHub Actions CI workflow
- **Session 15** — Desktop-only Selenium messaging
- **Session 14** — Render deployment config
- **Session 13** — Cold demo end-to-end on Firestore

---

## Next: Sessions 23–24 — TikTok/desktop job link + operator copy

Per [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md): Link TikTok desktop scrape jobs to research; operator-facing copy in UI explaining desktop-only flow. Pending desktop scrape without hanging Render.
