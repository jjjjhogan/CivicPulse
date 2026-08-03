# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Today — Session 4: Phase A hand gold sample (2026-07-24)

→ **Wrapping** — gold + failure modes ready for PR (see Done below when merged).

---

## Done — Week 1 Session 4 (2026-08-03)

Phase A **hand** gold sample (measurement only).

- [x] Branch `feature/phase-a-gold-hand-s4`; AI `review_batch_01.md` kept as draft only
- [x] Hand-label 96 signals (part A TikTok + part B mix)
- [x] Gold file: `data/labels/review_batch_02_hand.md` (+ `.json`)
- [x] Human tallies: correct 41 / partial 28 / none 20 / wrong 7
- [x] Failure modes 1–7 approved in `data/labels/failure_clusters_draft.md`
- [x] No keyword / classifier / Firebase / Research edits
- [x] Ready for PR → Session 5 Phase B uses this gold for re-score

### Session notes

- 2026-08-03: Promoted part A/B → gold. Human re-bucketed clusters (dropped empty 5/9; renumbered 1–7).

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
→ **Done** (hand gold + failure modes; see above). PR to merge.

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
