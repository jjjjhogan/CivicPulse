# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Today — Session 4: Phase A hand gold sample (2026-07-24)

**Theme:** Build a **human-labeled** gold sample so Session 5+ fixes are measured against real judgments — not an AI auto-pass.  
**Scope:** Measure only. **No** keyword surgery, model retrain, Firebase, or Research.

**Context:** Phase A audit work (PR #13 / `feature/phase-a-audit-s4`) produced an **AI-assisted** first pass now on `main` as [`data/labels/review_batch_01.md`](data/labels/review_batch_01.md) (~138 signals, auto verdicts). That file is a **draft / scaffold only**. It is **not** the gold sample until Jack + coworker have marked each row by hand.

### How we work today (one agent)

| Role | Job |
|------|-----|
| **One coding agent** | Prep the review worksheet, pull live signal text/IDs/method, keep tally + failure-mode notes, commit when asked. Does **not** invent correct/wrong/none labels. |
| **Jack + coworker (humans)** | Together, hand-classify each gold-sample signal: **correct / wrong / none / partial**; note obvious bad keywords or `method` when useful. |

No coworker/Jack code split this session — both people label; one agent supports the worksheet.

**Suggested branch:** `feature/phase-a-gold-hand-s4` (from current `main`). Prefer a new review file (e.g. `data/labels/review_batch_02_hand.md`) or clearly mark hand-verified rows in the draft so AI vs human judgments stay distinct.

### Agent prompt (copy/paste)

> Repo: CivicPulse (`Ryan/`). **Session 4 only** — Phase A **hand** gold sample.  
> Pull `main`. Use/create branch `feature/phase-a-gold-hand-s4`.  
> The AI first-pass in `review_batch_01.md` (if present) is draft only — do not treat its verdicts as ground truth.  
> Help Jack + coworker hand-label ~50–100 live signals (mix of sources). For each: show id, source, title/body snippet, assigned categories, `method`. Record **their** verdict (correct / wrong / none / partial) + short note.  
> After a solid batch: tally + top failure modes (still measurement only).  
> Do **not** edit `CATEGORY_KEYWORDS`, classifier, labels training set, Firebase, or Research.  
> `pytest -q` green if you touch tests; commit only when asked.

### Shared checklist

- [ ] Branch from latest `main`; draft AI review treated as scaffold only
- [ ] Hand-label gold sample (~50–100; mix TikTok / news / reddit / twitter / resident)
- [ ] Each row: verdict + note; capture `method` / bad keyword when obvious
- [ ] Save reusable hand review (`data/labels/review_batch_02_hand.md` or equivalent)
- [ ] Short failure-mode summary (enough to drive Session 5 Phase B)
- [ ] No keyword / model / Firebase / Research edits
- [ ] `pytest -q` green; PR when the hand sample is usable

### Session notes

-

### Shared done when

- [ ] Hand-labeled gold sample committed (reuse for Session 5 re-score)
- [ ] Failure modes written from **human** verdicts
- [ ] AI draft not confused with gold
- [ ] No Phase B scope creep

---

## Done — Week 1 Session 3 (2026-07-22)

Dashboard UX harden + offline-auth follow-up.

- [x] Feed / map / verify loading, empty, offline, error states (PR #12)
- [x] Scrapers-oriented job failure copy (as landed with UX harden)
- [x] Offline auth: stay on dashboard when API down (PR #14)
- [x] Reddit/Twitter import: lenient JSON + DevTools dump paste parser (PR #14)
- [x] Favicon `/favicon.ico` → `/favicon.svg`
- [x] `pytest -q` green on merge

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
→ **Done** (see above).

### Session 4 — Phase A measure (+ light test debt)
→ **Today** — hand gold sample (AI draft ≠ ground truth); see above.

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
