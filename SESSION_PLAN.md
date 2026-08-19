# CivicPulse — session plan (Sessions 27–28: Launch flow + real metrics)

**Goal:** Wire "Save draft" vs "Launch scrape" in the compose UI, and replace fake right-rail metrics with real archive data.

---

## Sessions 27–28 — Launch flow + real metrics

### Completed

**Backend (`routes/research.py`):**
- [x] `POST /api/researches/<id>/launch` — sets status to `gathering`, runs archive match, queues jobs for enabled sources
- [x] Launchable sources: `irvine-news` and `tiktok` (auto-start); twitter, reddit, youtube, facebook skipped as "not yet implemented"
- [x] Handles `scrapers_allowed` check — non-dev users still get archive match + gathering status, jobs gracefully skipped
- [x] Returns `{ research, archive_hits, jobs_started, jobs_skipped }`

**Backend (`routes/signals.py`):**
- [x] `/api/config` now includes `signal_count` and `signals_by_source` from real archive data

**Frontend (`research.js`):**
- [x] "Launch scrape" calls `POST /launch` with enabled sources list, then redirects to workspace
- [x] "Save draft" creates research and stays on compose page (unchanged behavior, now with button disable/re-enable)
- [x] Both buttons disable during submit to prevent double-clicks
- [x] Listen sources reordered: ready sources first (news311, tiktok), then archive-only (twitter, reddit, youtube, facebook)
- [x] `ready: true/false` flag on each source to distinguish live scrapers from archive-only
- [x] Listen grid shows "Archive only" badge on sources without live scrapers
- [x] Right rail metrics use real `signal_count` and `signals_by_source` from `/api/config`
- [x] "Voices" tile → shows signals in archive matching selected sources × time window
- [x] "Coverage" tile → shows % of total signals covered by selected sources
- [x] "Source status" tile (was "Compute cost") → shows "N of M sources live"
- [x] "First insight" tile → adjusts based on how many ready sources are enabled
- [x] Kicker changed from "Live preview — streaming" to "Estimate from archive"

**HTML (`research.html`):**
- [x] Metrics card labels updated: kicker, tile labels match real data semantics

**CSS (`research.css`):**
- [x] `.listen-badge` style for "Archive only" indicator

**Tests (`test_research_api.py`):**
- [x] `test_launch_research_sets_gathering` — launch sets status to `gathering`
- [x] `test_launch_skips_unimplemented_sources` — twitter/facebook/youtube skipped
- [x] `test_launch_research_not_found` — 404 for missing research
- [x] `test_launch_queues_news_job` — news311 source queues irvine-news job (dev_client)
- [x] All 156 tests pass

### Modified files

| File | Change |
|------|--------|
| `backend/routes/research.py` | `POST /api/researches/<id>/launch` endpoint |
| `backend/routes/signals.py` | `signal_count` + `signals_by_source` in `/api/config` |
| `research.js` | Launch flow, source badges, real metrics |
| `research.html` | Updated rail labels |
| `research.css` | `.listen-badge` style |
| `tests/test_research_api.py` | 4 new launch tests |

### Browser verification

- [x] Listen grid shows "Archive only" badges on 4 non-ready sources
- [x] Metrics rail shows "Estimate from archive" kicker
- [x] Metrics cite real signal counts (0 in empty DB, correct)
- [x] Source status tile updates when toggling sources (e.g. "2 of 2 sources live")
- [x] Save draft: creates research, clears form, shows "Draft saved.", stays on compose
- [x] Launch scrape: creates research, calls launch endpoint, redirects to workspace
- [x] Workspace shows status "gathering" after launch
- [x] No console errors on compose or workspace pages

---

## Exit criteria

- [x] Launch endpoint sets gathering + runs archive + queues jobs for implemented sources
- [x] Save draft stays on compose page
- [x] Unimplemented sources show "Archive only" badge
- [x] Right rail metrics cite real archive data, not hardcoded estimates
- [x] Metrics update reactively when toggles/window change
- [x] 156 tests pass
- [x] Browser verification

---

## Previous sessions

- **Sessions 25–26** — Research summary API + print/HTML
- **Sessions 23–24** — TikTok/desktop job link + operator copy
- **Sessions 21–22** — Research-scoped jobs (research_id FK, post-job matching, Jobs tab)
- **Sessions 19–20** — Topic keyword assist + category picker
- **Sessions 17–18** — Research workspace UI (PATCH/DELETE, tabs, inline edit, filters)
- **Session 16** — GitHub Actions CI workflow
- **Session 15** — Desktop-only Selenium messaging
- **Session 14** — Render deployment config
- **Session 13** — Cold demo end-to-end on Firestore

---

## Next: Sessions 29–30 — Summary extract flags + map filter by research

Per [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md): Summary uses extract flags (sentiment/clustering/policy sections); map filter pins by active research.
