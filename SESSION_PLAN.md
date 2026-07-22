# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Today — Session 4: Phase A classification audit (2026-07-22)

**Theme:** Empty / loading / error paths + readable scrape failures. **No redesign, no NLP, no Firebase, no Research.**  
**Why now:** Session 2 cold-start passed cleanly (unusually simple) — still do this pass so demos don’t look broken when the API is down or a job fails.

### Split

| Person | Focus |
|--------|--------|
| **Coworker** | Scrapers panel + job failure UX; stop-server / API-down behavior for scrapers |
| **Jack** | Feed, map, verify panel loading/empty/error; light CSS; optional favicon 404 note from soak |

Work on branch `feature/dashboard-ux-harden-s3` (or agree one shared branch). Keep PRs small; `pytest -q` still green.

---

### Coworker prompt (copy/paste)

> Repo: CivicPulse (`Ryan/`). **Session 3 only** — Dashboard UX harden.  
> Pull `main`, create/use branch `feature/dashboard-ux-harden-s3`.  
> Focus: **Scrapers panel** in `dashboard.js` / related CSS.  
> Goals:  
> 1) When a scrape job fails, show a **readable** `error` (and useful last log lines) — no raw Tracebacks/stack dumps in the panel UI.  
> 2) Status chips for running / done / failed stay clear.  
> 3) If the server is stopped mid-poll or `/api/jobs` returns 401/5xx, the scrapers UI fails **gracefully** (message, not a blank/broken panel).  
> Stay inside existing design language — light CSS only.  
> Do **not** change classifier, keywords, Firebase, or Research.  
> Manual test: start a news job then kill the server / force a failed job; confirm the UI stays understandable.  
> Leave notes under Session 3 “Coworker notes” in `SESSION_PLAN.md`. Commit on the feature branch when ready.

### Coworker checklist

- [ ] `git pull origin main` (+ sync feature branch if already created)
- [ ] Audit scrapers panel: running / completed / failed states
- [ ] `readableJobFailure` (or equivalent) never surfaces full stack traces in the panel
- [ ] Polling errors (network / 401 / 500) show a short user-facing message
- [ ] Manual: fail a job or stop server during poll → UI still usable
- [ ] `pytest -q` green
- [ ] Notes + commit on feature branch

### Coworker notes

-

---

### Your checklist (Jack) — see chat for full agent prompt

- [x] Feed: loading placeholder → live / empty notice / offline notice; "No signals match" when filters yield zero
- [x] Map: overlay message for offline, empty, and no-match-with-location states (centered on map, semi-transparent)
- [x] Verify panel: offline message; zero-reports shows "No resident reports yet" + link to report page; votes-load-failed notice
- [x] Light CSS only; fixed `/favicon.ico` 404 with 301 redirect to `favicon.svg` in Flask
- [x] Manual: simulated offline/empty/filter-no-match states in browser — all show graceful messages
- [x] `pytest -q` — 41 passed; awaiting coworker’s scrapers branch for merge coordination

### Shared done when

- [ ] Stop the API / break a job → dashboard still explains what happened (feed/map/verify/scrapers)
- [ ] No NLP/Firebase/Research scope creep
- [ ] Feature branch ready to PR into `main`

---

## Done — Week 1 Session 2 (2026-07-22)

Cold-start soak on coworker PC: **passed**.

- [x] import → reprocess → server → login → dashboard
- [x] `/api/signals` → `storage: "db"` (137+ signals)
- [x] Report + vote persist across reload
- [x] News job completed; TikTok skipped (no headed Chrome)
- [x] `pytest -q` — 41 passed
- Notes: favicon.ico 404 cosmetic only; no blockers

---

## Done — Week 1 Session 1

- [x] SQLite `/api/signals`, runbook, TikTok desktop harden
- [x] Reports + votes APIs, UI polish, pytest for new APIs

---

## How we work (quality bar)

1. One slice per session — shippable PR.
2. Done means demoed on this PC.
3. `pytest -q` green when behavior changes.
4. Docs in the same PR when ops change.
5. After any keyword/label change: **reprocess** + re-check the gold sample (Phase A).
6. Don’t start Firebase/Research UI before the week tables say so.

---

## Week 1 remaining

### Session 3 — Dashboard UX harden
→ **Today** (see above).

### Session 4 — Phase A measure (+ light test debt)
- [x] Gold sample — all 138 live signals reviewed; marked correct/wrong/none/partial
- [x] Method + failure-mode summary written (5 failure modes identified)
- [x] Saved as `data/labels/review_batch_01.md`
- [x] Added 5 edge-case tests for reports/votes (nonexistent signal, invalid choice, unauthenticated votes list, missing location, missing address) — 46 passed

**Results:** 34% correct, 25% wrong, 30% none (no civic content), 12% partial. Top failures: inherited TikTok comments (24% of total — chatter inherits parent category), legacy news labels (8/13 wrong), broad keywords ("waste" → sanitation, "housing" → university dorms). See `data/labels/review_batch_01.md` for full review.

---

## Week 2 (Sessions 5–8) — Phases B–D + Research spike

### Session 5 — Phase B keyword surgery + Phase D start
- [ ] Tighten/remove broad `CATEGORY_KEYWORDS` from Phase A failures
- [ ] `reprocess_signals` + re-score gold sample (before/after)
- [ ] UI: show **method**; soften/clarify confidence (not “accuracy %”)

### Session 6 — Phase C label batch #1
- [ ] Add hard/wrong + **none** examples to `labeled_signals.json`
- [ ] Reprocess; re-check gold sample
- [ ] Commit labels (+ any tiny keyword follow-ups)

### Session 7 — Research API spike (SQLite)
- [ ] `Research` create/list API (see roadmap product contract)
- [ ] Minimal UI to create a research by topic
- [ ] No Firebase yet

### Session 8 — Archive matcher + retro
- [ ] Keywords/categories → `research_hits` from existing signals
- [ ] Demo housing research; note remaining bad cats for Phase C #2
- [ ] Firestore schema sketch; name Session 9 owner

---

## Later (see roadmap)

- **Weeks 3–4:** Firestore → Render; Phase C continues  
- **Weeks 5–6:** Full Research workspace + gather jobs  
- **Weeks 7–8:** Summary, map-by-research, Phase D polish, demo freeze  
- **Phase E:** embeddings/stronger model — month 3 unless blocked  

---

**Roadmap:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md)
