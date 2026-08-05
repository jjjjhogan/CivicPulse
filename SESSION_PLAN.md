# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Next — Session 7.5: Phase C #2 hygiene (pre-archive)

**Goal:** Cut remaining live false positives before Session 8 archive matching — keyword tune, labels for hard/none cases, **manual remove or clear** junk signals, reprocess, re-score gold.

**Scope:** Phase C hygiene only. **No** Research UI, Firebase, or Phase E.

**Branch:** `feature/phase-c-hygiene-s7-5` (from latest `main`).

### Checklist

- [ ] Spot live FPs (dashboard / gold leftovers from Session 6 notes)
- [ ] Keyword tweaks in `CATEGORY_KEYWORDS` only where clearly justified
- [ ] Add hard/wrong/**none** rows to `labeled_signals.json` as needed
- [ ] Manual: delete or clear categories on obvious junk (lifestyle ads, non-civic fluff)
- [ ] `reprocess_signals` + sync DB; `rescore_gold.py` before/after
- [ ] `pytest -q` green; PR

### Agent prompt

> Repo: CivicPulse (`Ryan/`). **Session 7.5** — Phase C #2 hygiene before archive.  
> Pull `main`. Branch `feature/phase-c-hygiene-s7-5`.  
> Context: gold = `data/labels/review_batch_02_hand.*`; failures = `failure_clusters_draft.md`; Session 6 left ~9 none-verdict FPs (DB-only news, keyword/model hits).  
> Do: (1) tighten leftover broad keywords, (2) add none/hard labels, (3) manually remove or uncategorize junk signals in JSON/DB, (4) reprocess + rescore gold (don’t rewrite human verdicts), (5) short before/after note.  
> Don’t: Research API/UI, Firebase, embeddings, scrape-more-as-fix. Commit only when asked.

### Notes

-

---

## Week 2 status

| Session | Status |
|---------|--------|
| **5** Phase B + Phase D start | Done |
| **6** Phase C batch #1 + inheritance | Done |
| **7** Research API spike (SQLite) | Pending / parallel OK |
| **7.5** Phase C #2 hygiene | **Next** |
| **8** Archive matcher + retro | After 7.5 |

---

## Done — Sessions 1–4 (Week 1)

- S1–S3: platform, soak, UX harden (PRs #12–#14)
- S4: Phase A hand gold (PR #15) — `review_batch_02_hand.md`, clusters 1–7

### Session 5–6 (abbrev)

- **S5:** Broad housing/sanitation tokens → phrases; reprocess clear-on-empty; method/confidence UI; gold ~42%→47% correct.
- **S6:** +59 labels; `MIN_INHERIT_WORDS=5`; no legacy keep; `rescore_gold.py`; inheritance clusters addressed.

---

## How we work

1. One slice per session → PR.  
2. After keyword/label change: **reprocess** + gold re-score.  
3. `pytest -q` when behavior changes.  
4. No Firebase before the week table says so.

**Roadmap:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md)
