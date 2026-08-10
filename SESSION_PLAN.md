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

## Done — Session 9: Firestore project + emulator docs

**Branch:** `feature/firestore-s9-11`

### Build

- [x] `firebase.json`, `firestore.rules`, `firestore.indexes.json`
- [x] `backend/firestore.py` — lazy Firestore client via Firebase Admin SDK
- [x] `backend/config.py` — `DATA_BACKEND` env var (`sqlite` | `firestore`)
- [x] `.env.example` — Firestore env vars documented
- [x] `docs/FIRESTORE_SETUP.md` — full emulator setup guide
- [x] `requirements.txt` — `firebase-admin>=6.4.0`

### Exit

- [x] `firebase emulators:start --only firestore` documented
- [x] `pytest -q` green — 75 tests, 0 regressions

---

## Done — Session 10: Store interface + Firestore signals

**Branch:** `feature/firestore-s9-11`

### Build

- [x] `backend/store.py` — `SignalStore` protocol + `get_signal_store()` factory
- [x] `backend/store_sqlite.py` — SQLite implementation wrapping existing queries
- [x] `backend/store_firestore.py` — Firestore implementation
- [x] `backend/routes/signals.py` — `/api/signals` and `/api/signals/feed` use store
- [x] `DATA_BACKEND` switches between sqlite and firestore at runtime

### Exit

- [x] `/api/signals` works with `DATA_BACKEND=sqlite` (default)
- [x] `/api/signals` wired for `DATA_BACKEND=firestore` (Firestore store)
- [x] `pytest -q` green — 83 tests (8 new store tests: 4 SQLite, 4 Firestore mock)

---

## Done — Session 11: Port users, jobs, votes, reports to Firestore

**Branch:** `feature/firestore-s9-11`

### Build

- [x] `backend/store.py` — `UserStore`, `JobStore`, `VoteStore` protocols + factories + standalone job store
- [x] `backend/store_sqlite.py` — SQLite implementations for all resources
- [x] `backend/store_firestore.py` — Firestore implementations for all resources
- [x] `backend/auth.py` — uses `UserStore` instead of direct ORM queries
- [x] `backend/routes/auth.py` — signup/login/me use store, return dicts via `public_user()`
- [x] `backend/routes/reports.py` — create/list reports + votes use `SignalStore` + `VoteStore`
- [x] `backend/routes/jobs.py` — create/list/get/status use `JobStore`
- [x] `backend/jobs.py` — background runner uses `get_job_store_standalone()`

### Exit

- [x] Login/signup works with both backends
- [x] Vote casting/summary works with both backends
- [x] Job create/list/status works with both backends
- [x] Reports create/list works with both backends
- [x] `pytest -q` green — 104 tests (21 new store tests, 0 regressions)

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
| **9** Firestore project + emulator docs | Done |
| **10** Store interface + Firestore signals | Done |
| **11** Port users, jobs, votes, reports | Done |

---

## Earlier sessions (abbrev)

- **S1–S4:** platform, soak, UX, Phase A gold (PRs #12–#15)
- **S5:** keyword phrases; method/confidence UI; gold ~47%
- **S6:** +59 labels; inheritance gate; `rescore_gold.py`
- **S7.5:** FP hygiene; gold 40/78 (51.3%), 0 regressions
- **S7:** Research model + API (create/list/detail); 7 tests
- **S8:** Archive matcher + research_hits + detail Archive tab; 8 tests; housing demo 15 hits
- **S9:** Firestore project config + emulator docs; firebase-admin; DATA_BACKEND config
- **S10:** Store protocol (SignalStore) + SQLite/Firestore impls; /api/signals uses store; 8 new tests (83 total)
- **S11:** UserStore, JobStore, VoteStore; all routes use store abstraction; background job runner ported; 21 new store tests (104 total)

**Roadmap:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md)
