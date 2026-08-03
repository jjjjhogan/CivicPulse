# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Next — Session 5: Phase B keyword surgery + Phase D start

**Theme:** Kill worst false positives from Phase A gold failures; reprocess + re-score the **same** gold; start honesty in the UI (show `method`, soften confidence).  
**Scope:** Keyword hygiene + light inheritance guard if cheap + Phase D UI copy. **No** Firebase, Research, bulk `labeled_signals.json` (Session 6), or Phase E models.

**Depends on:** Session 4 gold on `main` — [`data/labels/review_batch_02_hand.md`](data/labels/review_batch_02_hand.md) (+ `.json`), failure modes in [`data/labels/failure_clusters_draft.md`](data/labels/failure_clusters_draft.md).

**Suggested branch:** `feature/phase-b-keywords-s5` (from latest `main`).

### Shared checklist

- [ ] Branch from latest `main` (Session 4 merged)
- [ ] Tighten/remove broad `CATEGORY_KEYWORDS` from gold clusters 4 + 7 (and clear keyword notes)
- [ ] Optional minimal inheritance guard for clusters 1 + 3 — or note deferral
- [ ] `reprocess_signals` (+ sync DB) + before/after re-score of **same** gold IDs
- [ ] UI: show **method**; soften/clarify confidence (not “accuracy %”)
- [ ] `pytest -q` green; PR when measurable gold improvement (or clear before/after write-up)

### Agent prompt (copy/paste)

> Repo: CivicPulse (`Ryan/`). **Session 5 only** — Phase B keyword surgery + Phase D start.  
> Pull latest `main` (confirm Session 4 gold is merged). Use/create branch `feature/phase-b-keywords-s5`.  
>  
> **Context from Session 4 (Phase A — DONE)**  
> - Human gold (NOT the AI draft): `data/labels/review_batch_02_hand.md` + `.json`  
> - 96 hand-labeled signals. Baseline: correct 41 (43%) | partial 28 (29%) | none 20 (21%) | wrong 7 (7%)  
> - AI draft `review_batch_01.md` is scaffold only — ignore its verdicts as ground truth  
> - Approved failure modes: `data/labels/failure_clusters_draft.md` (clusters 1–7)  
>   1. Inherited cats on non-civic TikTok comments (15) — `method=inherited`  
>   2. Non-civic should be uncategorized (11) — lifestyle/news fluff  
>   3. Inherited — video OK, comment weak/partial (12)  
>   4. Keyword match in non-civic context (7) — e.g. housing/rent on non-city issues  
>   5. Wrong category assignment (5)  
>   6. Model-only wrong rescues (2)  
>   7. Broad keyword false positives (3) — e.g. "waste"/"wasted", "mortgage"  
> - Worksheets: `batch_01_answers_part_a.txt` / `part_b.txt` (source of human notes)  
>  
> **Your job**  
> 1. From clusters 4+7 (and clear keyword notes in gold), tighten/remove broad `CATEGORY_KEYWORDS` in `scrapers/categories.py`. Prefer multi-word phrases over single tokens. Document each change briefly.  
> 2. Optionally address inherited chatter (clusters 1+3) with a minimal inheritance guard if low-risk; otherwise leave a short note — don’t expand scope.  
> 3. Run `scripts/reprocess_signals.py` and sync so live DB/JSON match.  
> 4. Re-score the SAME gold IDs: compare new assigned cats vs human verdicts in `review_batch_02_hand.json`. Write before/after tally (+ which failure modes improved). Do **not** rewrite human gold verdicts.  
> 5. Phase D start: UI shows classification `method`; soften/clarify confidence (match strength, not accuracy %).  
> 6. `pytest -q` green. Commit only when asked. One PR.  
>  
> **Do NOT**  
> - Edit Firebase / Research  
> - Bulk-edit `labeled_signals.json` (Session 6)  
> - Treat `review_batch_01.md` as gold  
> - Invent new architecture / embeddings (Phase E)  
> - Make “scrape more data” the session goal (optional targeted scrape only after keyword PR if needed for spot-check)

### Session notes

-

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
- [x] Merged as PR #15

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

### Sessions 3–4
→ **Done** (merged; Session 4 = PR #15).

---

## Week 2 (Sessions 5–8) — Phases B–D + Research spike

### Session 5 — Phase B keyword surgery + Phase D start
→ **Next** — full checklist + agent prompt above.

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
