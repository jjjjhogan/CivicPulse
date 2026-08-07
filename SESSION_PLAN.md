# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Done — Session 7.5: Phase C #2 hygiene (pre-archive)

**Goal:** Cut remaining live false positives before Session 8 archive matching — keyword tune, labels for hard/none cases, **manual remove or clear** junk signals, reprocess, re-score gold.

**Branch:** `feature/phase-c-hygiene-s7-5`

### Checklist

- [x] Spot live FPs (dashboard / gold leftovers from Session 6 notes)
- [x] Keyword tweaks in `CATEGORY_KEYWORDS` only where clearly justified
- [x] Add hard/wrong/**none** rows to `labeled_signals.json` as needed
- [x] Manual: delete or clear categories on obvious junk (lifestyle ads, non-civic fluff)
- [x] `reprocess_signals` + sync DB; `rescore_gold.py` before/after
- [x] `pytest -q` green; PR

### Notes

- **Before:** 38/78 (48.7%), 1 regression (id=128)
- **After:** 40/78 (51.3%), 0 regressions, 22 improvements, +4.3pp vs S5 baseline
- **Keywords:** replaced bare `accident` with compound phrases (`car accident`, `traffic accident`, `vehicle accident`, `fatal accident`, `accident scene`); removed broad `overpriced` from housing
- **Labels:** +17 examples (218 total, 55 negatives): legal ads, pet/vet posts, furniture giveaways, restaurant reviews, pharmacy, event listings, lost pet, staffing promo; +2 positives (city safety ranking, FBI scene)
- **Regression fix:** id=128 "city to raise a family" recovered — conflicting S6 negative replaced with distinct puff-news example
- **Model rescues:** 9→4 model-only after negatives strengthened `__none__` class

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
