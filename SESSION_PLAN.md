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

## Session 7 — Research API spike

**Goal:** Create/list Research via API + thin UI. No archive matching yet.

**Branch:** `feature/research-api-s7`

### Build

- [ ] `Research` model with: `title`, `topic`, `keywords[]`, `categories[]`, `status` (`draft` → …), timestamps, optional `notes` (`job_ids[]` can be empty)
- [ ] `POST /api/researches` — create
- [ ] `GET /api/researches` — list
- [ ] `GET /api/researches/<id>` — detail
- [ ] Minimal UI: create form + list (dashboard nav is enough)
- [ ] Same SQLAlchemy/SQLite patterns as other resources — no Firestore

### Exit

- [ ] Can create “Housing prices — Irvine” and see it listed
- [ ] `pytest -q` green for new routes/models
- [ ] PR

### Out of scope

Archive matcher, topic-scoped scrapes, summary/print, any storage-pipeline work.

---

## Session 8 — Archive matcher + Research detail

**Goal:** Archive pass attaches sensible existing signals (housing demo). Sketch Firestore needs in the PR notes only — no Firebase code.

**Branch:** `feature/research-archive-s8`  
**Depends on:** Session 7 merged (or stacked on top).

### Build

- [ ] Match rules (v1): category overlap with Research `categories[]` **and/or** keyword hit from `keywords[]` in signal title/body
- [ ] Persist `research_hits`: research id, signal id/key, match reason, timestamp
- [ ] `POST /api/researches/<id>/archive` — run against current signals read path
- [ ] Detail UI: **Archive** tab + click-through; empty/low-hit state that doesn’t look broken
- [ ] Manual QA: categories=`housing`, keywords like `rent` / `housing prices` → run archive → spot-check hits

### Exit

- [ ] “Housing prices” Research shows mostly plausible archive hits
- [ ] `pytest -q` for matcher + hits
- [ ] PR (optional one-line note: what Firestore would need later — sketch only)

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
| **7** Research API | **Next** |
| **8** Archive matcher | After 7 |

---

## Earlier sessions (abbrev)

- **S1–S4:** platform, soak, UX, Phase A gold (PRs #12–#15)
- **S5:** keyword phrases; method/confidence UI; gold ~47%
- **S6:** +59 labels; inheritance gate; `rescore_gold.py`
- **S7.5:** FP hygiene; gold 40/78 (51.3%), 0 regressions

**Roadmap:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md)
