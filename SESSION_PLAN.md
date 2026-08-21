# CivicPulse — session plan (Extend Research backend for new compose UI)

**Goal:** You (this agent) already shipped Sessions **23–32** — workspace, TikTok/desktop jobs, summary, demo path. A **new New Research compose UI** landed afterward (`research.html` / `research.js`). Extend **your** Research model, APIs, launch, metrics, and summary so those UI controls are real product inputs—not cosmetic.

**Canonical plan:** [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md) Weeks 7–8 Sessions **25–29**.

---

## Situation (read before coding)

| Layer | Status |
|-------|--------|
| Your Sessions 23–32 stack | **Done** — keep workspace, archive match, research-scoped jobs, summary/print. Extend these; do not rebuild. |
| New compose UI | **Shipped by teammate** — treat as the product contract. Layout stays; do not redesign. |
| Backend vs UI | **Mismatch** — Research create still expects old fields. UI sends listen/extract/window mostly via `notes` (`composeNotes()` in `research.js`). |
| Extract / live preview | **UI-only today** — checkboxes and metrics rail do not drive your summary or estimates yet. |

**UI features your backend must support:**

- `time_window`, `geo_radius`, `languages[]`
- `listen_sources[]` (toggles: twitter, reddit, youtube, tiktok, news311, facebook)
- `extract[]` (checkboxes: sentiment, clustering, demographics, policy, misinfo, bots)
- Suggested expansions from title (voice + civic chips → `keywords` / `categories`)
- Save draft vs Launch scrape
- Live preview estimates (replace client mock with real denominator)
- Summary/print sections gated by `extract[]`

**Do not:** redesign compose HTML/CSS, template CMS, live ethics engine, or real bot/misinfo ML. Honest “not implemented” for scrapers you don’t have yet.

---

## Agent prompt (paste for the Sessions 23–32 agent)

```
You already finished CivicPulse Research Sessions 23–32 (workspace, jobs linked to research, archive matching, summary/demo path). A teammate shipped a new New Research compose UI afterward. Your job is to EDIT AND EXTEND THE BACKEND (and minimal research.js glue) so that UI’s new features are first-class — not notes text or mocks.

READ FIRST
- Compose contract: research.html + research.js (LISTEN_SOURCES, EXTRACT_OPTIONS, selectors, buildPayload/composeNotes).
- Your existing Research APIs, stores, job launch, summary/print.
- docs/TWO_MONTH_ROADMAP.md Weeks 7–8 Sessions 25–29.
- DATA_BACKEND may be sqlite or firestore — update both store impls + tests.

MINDSET
- Backend is the source of change. Touch research.js only to POST/GET the new fields, call new endpoints, and drop composeNotes() serialization of listen/extract/window.
- Do not redesign the compose page or rebuild research-detail.
- Reuse your archive matcher, POST /api/jobs?research_id, and summary/print.

REQUIRED WORK (in order)

1) Persist compose config on Research (Session 25)
- Add fields: time_window, geo_radius, languages[], listen_sources[], extract[].
- Migrate SQLite model; update Firestore ResearchStore + store protocol + to_dict.
- POST/PATCH/GET /api/researches round-trip these fields.
- research.js: send them as JSON fields; stop stuffing into notes.
- pytest create/get/patch for the new fields.

2) Expansions endpoint (Session 26)
- Add suggest/expansions API from title → { voice_chips, civic_chips, categories } using category_keywords (+ move or mirror research.js VOICE_EXTRAS server-side).
- Point research.js idle/blur at that API; keep custom chips.

3) Draft vs launch honors listen_sources (Session 27)
- Draft: persist config, no scrape queue.
- Launch: status gathering (or your existing equivalent), archive match, queue jobs only for listen_sources that are ON and that your stack already implements (news / tiktok). Others: “armed, not implemented” — no fake jobs.
- Facebook stays off by default. Land in research-detail with hits + real job when applicable.

4) Preview metrics from real counts (Session 28)
- Replace client-only mock estimates with API (or signals count) × enabled sources × time_window. Still labeled estimate. Ethics gate static; templates form-fill only.

5) extract[] gates your summary (Session 29)
- Update YOUR summary/print path: omit sections for unchecked extract flags (sentiment, clustering, policy, etc.).
- No new ML for bots/misinfo — section inclusion / placeholder copy only.

CONSTRAINTS
- Minimal diffs; match your existing style.
- pytest -q green.
- No secrets. No compose redesign.
- Tick Sessions 25–29 in docs/TWO_MONTH_ROADMAP.md when done.

EXIT
- GET research returns compose fields; UI round-trips them.
- Launch respects listen_sources against your job runners.
- Live preview uses a real signal/archive denominator.
- Summary respects extract[].
- Note completion under Completed in SESSION_PLAN.md.
```

---

## Checklist

### Persist (25)
- [x] Research model/stores/API: `time_window`, `geo_radius`, `languages`, `listen_sources`, `extract`
- [x] `research.js` posts real fields (not `notes` dump)
- [x] Tests pass

### Expansions (26)
- [x] Backend suggest API
- [x] Compose calls it on title idle/blur

### Launch (27)
- [x] Draft vs launch
- [x] Jobs only for enabled + implemented sources

### Metrics (28)
- [x] Preview endpoint/estimate from real counts

### Summary (29)
- [x] Your summary/print gated by `extract[]`

### Verify
- [x] `pytest -q` — 161 passed
- [x] Browser: compose → draft → launch → workspace → summary reflects extract + listen
- [x] Roadmap checklist 25–29 updated

---

## Out of scope

- Redesigning `research.html` / compose CSS
- Sessions 31–32 human demo polish
- New Twitter/Reddit/YouTube/Facebook scrapers
- Real ethics/PII scanners or bot/misinfo models

---

## Key files

| Focus | Files |
|-------|--------|
| **Extend (primary)** | `backend/models.py`, `backend/migrate.py`, `backend/routes/research.py`, `backend/store*.py`, summary/print routes you added in 23–32, `backend/routes/jobs.py` / `backend/jobs.py` |
| **Glue (minimal)** | `research.js` (payload + API calls only) |
| **Contract (read-only layout)** | `research.html`, `research.css` |
| **Reuse** | `research-detail.*`, `backend/research_match.py` |
| **Tests** | `tests/test_research_api.py` (+ summary tests if you have them) |

---

## History

- You: Sessions **23–32** Research stack complete
- Teammate: New compose UI shell on `research.html`
- This pass: Backend catches up to that UI (Sessions **25–29** glue)
