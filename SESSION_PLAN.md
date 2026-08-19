# CivicPulse — session plan (Sessions 31–32: Phase D polish + demo freeze)

**Goal:** Confidence honesty (Phase D), hardening, operator/demo seed, and feature freeze with demo rehearsal script.

---

## Sessions 31–32 — Phase D polish + demo freeze

### Completed

**Phase D — Confidence honesty (`signal.js`):**
- [x] Signal detail page: replaced raw percentage chip (e.g. "82%") with qualitative band ("Strong" / "Moderate" / "Weak")
- [x] Percentage now only in tooltip: `Match strength: 82%`
- [x] Added method chip (keywords / model / keywords + model / inherited / outlet default) before the confidence band, matching feed card pattern
- [x] Feed cards (dashboard.js) already used qualitative labels — no change needed there

**Phase D — Source analytics (`source.js`):**
- [x] Replaced "avg confidence: 72%" stat tile with qualitative "Moderate" / "Strong" / "Weak"
- [x] Renamed stat label from "avg confidence" to "match strength"

**Hardening:**
- [x] Walked compose → workspace → summary flow in browser
- [x] Empty states verified: archive panel shows "No matching signals yet", map shows "No signals matched yet", summary shows "0 signals"
- [x] No JS errors besides expected 401 on auth/me (not logged in)
- [x] Tab switching (Archive / Map / Jobs / Summary) all correct

**Demo seed (`scripts/seed_demo.py`):**
- [x] Creates 3 demo researches (housing, potholes, public safety) with categories, keywords, and extract flags
- [x] Runs archive match to populate hits
- [x] `--check` flag reports current DB counts without modifying
- [x] Skips if demo researches already exist (idempotent)

**Demo script (`docs/DEMO_SCRIPT.md`):**
- [x] 10-minute walkthrough: dashboard → source analytics → compose → workspace → print summary
- [x] Talking points for Q&A (accuracy, data sources, privacy, scraper access)
- [x] Pre-demo checklist

**Tests:**
- [x] All 160 tests pass (29 in research API)
- [x] Browser verified: confidence chips show qualitative labels, source analytics shows "match strength", compose → workspace flow clean

### Modified files

| File | Change |
|------|--------|
| `signal.js` | Qualitative band + method chip on detail page |
| `source.js` | "match strength" qualitative label instead of avg % |
| `scripts/seed_demo.py` | New: demo database seeder |
| `docs/DEMO_SCRIPT.md` | New: 10-minute mayor demo script |

### Browser verification

- [x] Dashboard feed cards: 20 conf chips, all qualitative (Strong/Moderate/Weak), zero raw %
- [x] Source analytics: "Moderate" for "match strength" (was "72%" for "avg confidence")
- [x] Compose → save draft → workspace renders with all 4 tabs
- [x] Archive empty state message clear
- [x] Map tab initializes Leaflet map
- [x] Summary tab loads preview
- [x] No console errors

---

## Exit criteria

- [x] No "92% wrong" moments — confidence shown as qualitative bands
- [x] Method always surfaced (detail page + feed cards)
- [x] Demo seed script creates researches with archive hits
- [x] 10-minute demo script written
- [x] 160 tests pass
- [x] Browser verification clean

---

## Previous sessions

- **Sessions 29–30** — Extract flags + map view
- **Sessions 27–28** — Launch flow + real metrics
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

## Status: Feature freeze

Sessions 31–32 mark feature freeze. The compose → workspace → summary → print flow is complete. Remaining work is bug fixes, demo rehearsals, and Phase C label batches for classifier accuracy.
