# CivicPulse — session plan (day-to-day)

**For:** next-session checklists and prompts to your coworker / coding agent.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

**Pace:** One theme per session → PR → manual QA → merge.

**North star:** Research workspace on **Firestore** → **Render**; plus **classifier quality loop** (Phases A–E) so categories are trustworthy enough for demos.

---

## Next — Session 7: Research API spike (SQLite)

**Theme:** Build the Research create/list API on SQLite and a minimal UI to create a research by topic.  
**Scope:** Research API + basic UI. **No** Firebase, advanced classifier work, or Phase E models.

**Depends on:** Sessions 5+6 merged.

**Suggested branch:** `feature/research-api-s7` (from latest `main`).

### Shared checklist

- [ ] `Research` create/list API (see roadmap product contract)
- [ ] Minimal UI to create a research by topic
- [ ] No Firebase yet
- [ ] `pytest -q` green; PR when API works end-to-end

### Session 5 notes

- Keyword surgery: removed broad single-token keywords from `housing` (rent, mortgage, apartment, housing, lease) and `sanitation` (waste). Replaced with multi-word phrases (rent price, rent control, housing cost, waste collection, etc.). Targets clusters 4+7.
- Reprocess fix: `reclassify_row()` now clears categories when old method was `keywords`/`keywords+model` and new classifier returns nothing (instead of preserving as `legacy`).
- Re-score (79/96 matched, 17 unmatched due to DB reimport): correct 42%→47%, 5 FPs fixed, 0 regressions.
- Clusters 1+3 (inherited chatter): **deferred to Session 6**. Fixing inheritance requires checking whether comment text has civic content before inheriting video categories — touches `tiktok/export.py` and `reprocess.py` with non-trivial edge cases (partial civic comments, short reactions). Too risky for a keyword-only session. The 27 affected signals are all `partial` or `wrong` verdicts on TikTok comments; keyword surgery doesn't help since their method is `inherited`, not `keywords`.
- Phase D UI: method chip visible on cards, confidence shows "Strong"/"Moderate"/"Weak" (not raw %), tooltip says "Match strength: XX%", rescued badge says "model catch".

### Session 6 notes

- **Training data:** Added 59 examples to `labeled_signals.json` (142→201 total). Breakdown: 22 negatives (18→40), 10 public_safety (10→30, was weakest), 3 emergencies, 3 traffic_safety, 2 violent_crime, 3 immigration, 3 property_crime, 11 multi-category (0→11), 3 hard cases. All categories now 14+ examples.
- **Inheritance guard:** `MIN_INHERIT_WORDS=5` in `classifier.py`. Comments with < 5 content words no longer inherit video categories — applied in both `reprocess.py` (consensus + inherited_from_video branches) and `tiktok/export.py`. Cleared 35+ non-civic TikTok reactions ("lol same", "well well well", emoji-only comments).
- **Legacy fallback removed:** `reclassify_row()` now clears ALL old categories when the current classifier returns nothing, regardless of old method. Previously only cleared `keywords`/`keywords+model`; now also clears `legacy`, empty-method, and other stale assignments.
- **Re-score script:** New `scripts/rescore_gold.py` automates gold comparison (matches by URL+title/body, checks JSON first then DB fallback).
- **Re-score (78/96 matched, 18 unmatched):** 0 regressions on 24 correct-verdict signals. 22 improvements: 5 wrong-verdict signals changed (4 cleared, 1 added correct category), 17 partial-verdict signals changed (16 cleared non-civic chatter, 1 reduced overassignment). Conservative metric: 35/78 (44.9%). 9 none-verdict false positives remain: 5 DB-only news (legacy, not in JSON for reprocessing), 2 keyword FPs (homeless story, Irvine Company mention), 2 model FPs (restaurant review, Korean housing ad).
- **Clusters 1+3 addressed:** Inheritance guard directly fixes the 27 deferred signals (short TikTok chatter). Most short comments now correctly uncategorized.
- **Tests:** 56 tests (up from 51). New tests: event listing negative, housing ad negative, multi-category, short inherited comment cleared, long inherited comment keeps categories, legacy categories cleared.

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
→ **Done** — branch `feature/phase-b-keywords-s5` (PR pending).

### Session 6 — Phase C label batch #1
→ **Done** — branch `feature/phase-c-labels-s6`.
- [x] Added 59 training examples to `labeled_signals.json` (142→201)
- [x] Inheritance guard for clusters 1+3 (MIN_INHERIT_WORDS=5)
- [x] Removed legacy category fallback
- [x] Reprocessed; re-checked gold sample
- [x] `pytest -q` green (56 tests, up from 51)

### Session 7 — Research API spike (SQLite)
→ **Next** — full checklist + agent prompt above.

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
