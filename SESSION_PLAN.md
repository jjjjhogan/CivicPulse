# CivicPulse — session plan (Path A: Research)

**For:** Path A coworker / coding agent — Research product sessions.  
**Not** the 8-week strategy — that lives in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).  
**Not** Path B (data durability / DB rewiring) — separate owner; this file only says what Path A must **avoid**.

**Pace:** One theme per session → PR → manual QA → merge.

**Goal:** Mayor can create a Research (e.g. “housing prices in Irvine”) and see **archive hits** from existing signals.

---

## Stay off (do not touch)

Someone else owns storage durability. Path A must **not**:

- Redesign SQLite schema / add a new store abstraction / Firestore
- Change orphan prune, backup/restore, or scrape→JSON→DB sync
- Delete or reshape `data/signals/*` / `data/raw/*` for storage experiments
- Run classifier keyword surgery or `reprocess_signals` unless explicitly asked
- Add cleanup scripts, schema drops, or silent data deletes

**If Research seems to need better persistence:** stub on today’s Signal table / `/api/signals`, leave a one-line note for Path B, and move on.

---

## Agent prompt (Path A)

Copy into a new agent chat:

```text
Repo: CivicPulse (Ryan/). You are on Path A — Research product only.

Read SESSION_PLAN.md and follow Session 7 first, then Session 8.

Do:
- Session 7: Research model + POST/GET /api/researches (+ detail) and a minimal create/list UI, using the same SQLAlchemy/SQLite patterns as existing resources.
- Session 8: Archive matcher → research_hits + POST archive endpoint + Research detail Archive tab. Demo topic: “housing prices in Irvine” using existing live signals.
- pytest -q for anything you add. One PR per session slice.

Do NOT:
- Redesign or rewire the database, prune/backup pipelines, or scrape→JSON→DB flow.
- Touch Firebase/Firestore/Render.
- Delete or rewrite signal/raw data files.
- Change classifier keywords or run reprocess unless the user explicitly asks.
- Mix Path B / data-durability work into your PR.

If persistence feels insufficient, stub against current /api/signals + existing models and note a follow-up — do not invent a second database story.
```

---

## Preconditions (done)

- [x] Sessions 5–6 classifier loop
- [x] Session **7.5** hygiene (fewer live FPs before archive demos)
- [x] Small civic housing batch exists for demos (corpus still thin — Archive UI must handle low hit counts)

Use existing housing signals for the demo. Prefer matcher/UI filters over global classifier changes if hits look noisy.

---

## Done — Session 7: Research API spike

**Branch:** `feature/research-api-s7`

### Build

- [x] `Research` model (title, topic, keywords[], categories[], status, notes, timestamps)
- [x] `POST /api/researches` — create
- [x] `GET /api/researches` — list
- [x] `GET /api/researches/<id>` — detail
- [x] Minimal UI: create form + list + detail page, dashboard sidebar link
- [x] Same SQLAlchemy/SQLite patterns — no Firestore

### Exit

- [x] Can create “Housing prices — Irvine” and see it listed
- [x] `pytest -q` green — 7 new API tests (67 total)
- [x] PR pushed

---

## Done — Session 8: Archive matcher + Research detail

**Branch:** `feature/research-api-s7` (stacked on Session 7)

### Build

- [x] Match rules (v1): category overlap + keyword hit (\b word-boundary) in title/body, scored 0.5/cat + 0.3/kw
- [x] `ResearchHit` model: research_id, signal_id, match_reason, score, timestamp (unique constraint)
- [x] `POST /api/researches/<id>/archive` — runs matcher, persists hits, sets status=active
- [x] Detail UI: Archive tab with hit cards (score, source, categories, match reason, click-through)
- [x] Manual QA: “housing prices in Irvine” → 15 hits, top results are housing-categorized + rent-keyword signals

### Exit

- [x] Housing Research shows plausible archive hits — top 2 are category+keyword combos (score 0.8)
- [x] `pytest -q` green — 8 new archive tests (75 total)
- [x] PR pushed. Firestore note in commit message.

### Out of scope

Firebase/Render, import/prune/backup rewrites, new gather jobs, embeddings, classifier keyword passes.

---

## Working rules

1. One slice per session → PR (API before big UI).
2. Read signals the same way the dashboard does (`/api/signals` / existing models).
3. `pytest -q` when behavior changes.
4. Never ship orphan-delete / cleanup / schema-drop work on Path A branches.

---

## Status

| Session | Status |
|---------|--------|
| **5–6** Classifier loop | Done |
| **7.5** Hygiene | Done |
| **7** Research API | Done |
| **8** Archive matcher | Done |

---

## Earlier sessions (abbrev)

- **S1–S4:** platform, soak, UX, Phase A gold (PRs #12–#15)
- **S5:** keyword phrases; method/confidence UI; gold ~47%
- **S6:** +59 labels; inheritance gate; `rescore_gold.py`
- **S7.5:** FP hygiene; gold 40/78 (51.3%), 0 regressions
- **S7:** Research model + API (create/list/detail); 7 tests
- **S8:** Archive matcher + research_hits + detail Archive tab; 8 tests; housing demo 15 hits

**Roadmap:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md)
