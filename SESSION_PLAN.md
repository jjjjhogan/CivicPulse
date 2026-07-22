# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E in the roadmap) so categories are trustworthy enough for demos.

---

## Today — Coworker Session 2 (2026-07-22)

**Owner:** coworker  
**Goal:** Cold-start CivicPulse on **his machine** with **SQLite**, prove the dashboard works end-to-end. **No new features** — soak + note bugs only.

### Coworker prompt (copy/paste)

> Repo: CivicPulse (`Ryan/`). Do **Session 2 only** from `SESSION_PLAN.md`.  
> Cold-start on this PC with SQLite: venv → pip → import → reprocess → dashboard_server → login → dashboard.  
> Verify `/api/signals` shows `"storage": "db"`. Submit one resident report and one vote; reload and confirm they persist.  
> Optional if time: one news job from Scrapers panel (skip TikTok unless headed Chrome is set up).  
> Fix only blockers that prevent the cold start. No Firebase, Research UI, or classifier rewrite.  
> Write any failures as bullets under “Soak notes” in `SESSION_PLAN.md` and commit if you fixed something.

### Checklist

#### A. Pull latest & set up
- [ ] `git pull origin main`
- [ ] `python -m venv .venv` (if no venv yet)
- [ ] Activate venv: `.\.venv\Scripts\Activate.ps1` (Windows) or `source .venv/bin/activate`
- [ ] `pip install -r requirements.txt`
- [ ] `copy .env.example .env` (optional; defaults are fine for local SQLite)

#### B. Load SQLite & run server
- [ ] `python scripts/import_signals.py`
- [ ] `python scripts/reprocess_signals.py`
- [ ] `python scripts/dashboard_server.py`
- [ ] Open http://127.0.0.1:8080/login.html — **create an account**, then open the dashboard

#### C. Verify DB-backed dashboard
- [ ] http://127.0.0.1:8080/api/signals → JSON includes `"storage": "db"` and a non-zero `count`
- [ ] Dashboard feed/map show live signals (not only empty/broken UI)
- [ ] Submit one report via `report.html` → appears after dashboard refresh
- [ ] Cast one vote on a resident report in Verify → reload → vote tallies still there

#### D. Optional soak (if time)
- [ ] One **news** job from Scrapers panel → job completes or fails with a readable message
- [ ] TikTok only if Chrome is available; headed, short run — do not debug Selenium deeply today
- [ ] `pytest -q` green

#### E. Wrap-up
- [ ] Add **Soak notes** below (what worked / what broke)
- [ ] If you fixed a blocker: commit on a branch or main per team habit and push
- [ ] Do **not** start Session 3 / Phase A / Firebase today unless Session 2 is fully green

### Soak notes (coworker fills in)

- Date / machine:
- Cold start OK? (Y/N)
- `/api/signals` storage:
- Report + vote persist? (Y/N)
- Bugs / blockers:
-

**Done when:** Coworker can demo login → dashboard → DB signals from a fresh terminal without asking for help.

---

## Done — Week 1 Session 1 (do not re-open unless regressing)

- [x] SQLite `/api/signals`, runbook, TikTok desktop harden
- [x] Reports + votes APIs, UI polish, pytest for new APIs

---

## How we work (quality bar)

1. One slice per session — shippable PR.
2. Done means demoed on this PC.
3. `pytest -q` green when behavior changes.
4. Docs in the same PR when ops change.
5. After any keyword/label change: **reprocess** + re-check the **gold sample** (Phase A list).
6. Don’t start Firebase/Research UI before the week tables say so.

---

## Week 1 remaining (Sessions 2–4)

### Session 2 — Platform soak + docs polish
→ **In progress today** (see “Today — Coworker Session 2” above).

- [ ] Cold-start: import → reprocess → server → login → dashboard
- [ ] Report + vote persist; `/api/signals` → `storage: "db"`
- [ ] Short TikTok + one news job; fix only soak bugs
- [ ] Smoke checklist in README or `docs/` (use README cold-start section; expand only if gaps found)

### Session 3 — Dashboard UX harden
- [ ] Empty/loading/error for feed, map, verify, scrapers
- [ ] Readable job `error` + log (no stack dumps in panel)
- [ ] Light CSS only

**Prompt:** Session 3 only — failure UX. No NLP changes.

### Session 4 — Phase A measure (+ light test debt)
- [ ] Gold sample ~50–100 live signals; mark correct/wrong/none
- [ ] Note `method` + obvious bad keywords; write failure-mode summary
- [ ] Save review list for reuse (sheet or `data/labels/review_batch_*.md`)
- [ ] Optional: small reports/votes test gaps if time

**Prompt:** Phase A only — measure classification errors. Do not edit keywords/model yet unless a one-line typo. No Firebase/Research.

**Done when:** Reusable gold sample + top failure modes written down.

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

## Later (see roadmap tables)

- **Weeks 3–4:** Firestore → Render; Person B continues Phase C batches  
- **Weeks 5–6:** Full Research workspace + gather jobs  
- **Weeks 7–8:** Summary, map-by-research, Phase D polish, demo freeze  
- **Phase E:** embeddings/stronger model — month 3 unless blocked  

---

**Roadmap:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md)
