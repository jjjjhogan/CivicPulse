# CivicPulse — session plan (Research = query the signal aggregate)

**Product rule:** New Research **never** starts external scrapes. Scrapers (TikTok, news, etc.) stay on the Scrapers / `is_dev` operator path and fill the shared signal store. Research only **searches and analyzes signals already in the database** (Firestore/SQLite). A legislator configures a topic, then CivicPulse “listens” and “extracts” against that aggregate.

**UI copy:** Rename **Launch scrape** → **Launch research** everywhere on the compose page.

**Canonical north star:** Large civic-signal corpus → Research over that corpus → briefing for mayor/staff. See also [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).

---

## Situation (read before coding)

| Layer | Current | Target |
|-------|---------|--------|
| Compose “Launch scrape” | Implies external ingest | **Launch research** — archive pass + extract tools only |
| `/api/researches/<id>/launch` | Lists `queued_sources` as if jobs will run; does not (and must not) call scrapers | Run **archive match** filtered by listen/window/geo/lang; then run **extract tools** for checked `extract[]` |
| `listen_sources` | Saved; used for preview math; fake “queue” | **Filter** which signal `source`s (and related outlets) count as “where we listen” in the archive |
| `extract[]` | Saved; summary API stubs; **not shown** in workspace | Each checkbox maps to a **tool** that transforms archive hits → summary sections / workspace panels |
| Jobs tab on research-detail | Start news/TikTok scrape from research | **Remove or hide scrape-from-research.** Jobs for scrapes live under Scrapers only. Optional later: show “last ingest that grew the pool” as read-only context — not launched from Research |

**Do not:** queue `POST /api/jobs` from Research compose or detail. Do not build Twitter/Reddit scrapers “for research.” Do not redesign the whole compose layout—fix the contract and wire tools.

---

## Agent prompt (paste into Cursor)

```
CivicPulse Research must stop behaving like a scrape launcher. Edit the product so Research only queries and analyzes signals already in the DB. External scrapes remain a separate operator flow (scrapers.html / is_dev).

PRODUCT CONTRACT
1. Rename UI: “Launch scrape” → “Launch research” (research.html button, any matching copy in research.js / research-detail).
2. Launch research = (a) archive match over existing signals, (b) apply listen_* filters, (c) run extract tools for checked extract[]. NEVER call job start / scrape APIs from Research.
3. Where to listen (listen_sources): filter which stored signal sources participate (map UI ids → DB source values, e.g. news311→news, tiktok→tiktok, twitter→twitter, reddit→reddit). Unimplemented sources in the corpus simply contribute 0 hits — honest empty state, not a scrape queue.
4. time_window / geo_radius / languages: filter archive matching when fields exist on signals (published_utc, metadata geo/lang, outlet heuristics). Soft filters OK if geo/lang sparse; document behavior.
5. What should CivicPulse extract: each checkbox is a TOOL over matched hits. Build real (even if v1-simple) tools — not only “placeholder note” strings. Wire results into GET summary AND show them on research-detail (Summary tab or panel). Unchecked = tool not run / section omitted.
6. Save draft: persist compose fields, no archive run required (or optional light preview). Launch research: status gathering→ready (or your existing statuses), replace hits, persist extract outputs, open workspace.

EXTRACT TOOLS TO IMPLEMENT (v1 — rule/heuristic OK; no giant new ML stack required)
Create a clear module e.g. backend/research_extract.py (or tools under backend/research_tools/) with one function per flag:

- sentiment: score/label each hit or aggregate supportive/mixed/critical from body/title heuristics (lexicon or existing classifier signals). Return counts + sample quotes.
- clustering: group hits into 5–20 narrative clusters (start with category + keyword co-occurrence or simple embedding-free clustering by shared keywords). Return cluster labels + sizes + top snippets.
- demographics: v1 = inferred buckets only when metadata allows; otherwise “insufficient signal” with counts of labeled vs unknown — no fake people.
- policy: extract imperative / “should/need/want the city to…” style asks from bodies; return list of asks with source hit ids.
- misinfo: flag claims that conflict with a small allowlist of city-checkable patterns OR mark “needs fact-check” when high-certainty civic numbers appear; keep conservative.
- bots: v1 = coordination heuristics (duplicate body, burst timing if timestamps exist); filter or flag hits — document false-positive risk.

LISTEN FILTERS
- On archive match, intersect candidates with listen_sources mapping before writing research_hits.
- Preview metrics (live rail): estimate from COUNT of signals matching listen_sources × time_window — still labeled estimate, but denominator = real DB.

REMOVE / DISABLE
- research launch must not return queued scrapes as if jobs will start; remove scrape-queue language.
- research-detail: remove “Start Job” scrape controls from Research (or gate behind a clearly separate operator page only). If coworker added research_id job linking for scrapes, keep the DB field for historical jobs but do not offer start-from-research in the legislator UI.
- Update SESSION_PLAN / roadmap notes: Research ≠ scrape.

API SHAPE (suggested)
- POST /api/researches (draft) — persist compose fields including listen_sources, extract, time_window, geo_radius, languages.
- POST /api/researches/<id>/launch — archive match + run extract tools; store results (e.g. research.extract_results JSON or subcollection); no jobs.
- GET /api/researches/<id>/summary — sections built from extract_results / tools, gated by extract[].
- Keep POST /api/jobs only on scrapers routes for is_dev operators.

FRONTEND
- research.js: button label Launch research; launch endpoint only; show skipped/empty listen sources honestly if no signals of that type exist.
- research-detail.js: Summary panel rendering sections from /summary; drop scrape start UI from this page.
- Minimal CSS for summary sections.

TESTS
- Launch does not create scrape jobs.
- listen_sources filters hits by source.
- Each extract flag adds/omits the corresponding summary section; with flag on, section has structured data (not only a placeholder string) for at least sentiment + clustering + policy in v1.
- pytest -q green.

CONSTRAINTS
- Match existing style; both SQLite and Firestore stores.
- No secrets. No compose visual redesign beyond copy + wiring.
- Tick progress in this SESSION_PLAN.md when done.

EXIT
- Legislator can compose → Launch research → see archive hits from DB only → summary changes when extract checkboxes change → where-to-listen changes which sources appear in hits.
- Zero path from Research UI to Selenium/news scrape process.
```

---

## Checklist

### Product / copy
- [ ] “Launch scrape” → **Launch research**
- [ ] Docs/comments: Research queries aggregate; scrapes are separate

### Launch path
- [ ] `/launch` runs archive match + extract tools only
- [ ] No `POST /api/jobs` / `start_job` from Research compose or detail
- [ ] Remove or hide Start Job scrape UI on `research-detail`

### Where to listen
- [ ] `listen_sources` filters which DB `source`s enter `research_hits`
- [ ] Empty source = empty contribution (not “queue scrape”)
- [ ] Preview metrics use real filtered counts

### Extract tools (build each)
- [ ] `sentiment` tool → summary + workspace
- [ ] `clustering` tool → summary + workspace
- [ ] `demographics` tool (honest sparse v1)
- [ ] `policy` tool → list of asks
- [ ] `misinfo` tool (conservative v1)
- [ ] `bots` tool (heuristic v1)
- [ ] Unchecked flags omit sections / skip tools

### Verify
- [ ] `pytest -q`
- [ ] Browser: toggle listen sources → different hit mix; toggle extract → different summary; Launch research never opens Chrome / news job

---

## Out of scope

- New external scrapers for Research
- Template CMS / live ethics engine
- Perfect ML for demographics/misinfo/bots (v1 heuristics + honesty OK)

---

## Key files

| Focus | Files |
|-------|--------|
| Compose | `research.html`, `research.js` |
| Workspace | `research-detail.html`, `research-detail.js` |
| Launch / summary | `backend/routes/research.py` |
| New tools | `backend/research_extract.py` (or `backend/research_tools/*`) |
| Matching | `backend/research_match.py` (add source/window filters) |
| Stores | `backend/models.py`, `backend/store*.py`, migrate if storing `extract_results` |
| Scrapers (leave alone for Research) | `scrapers.html`, `backend/routes/jobs.py` |
| Tests | `tests/test_research_api.py` (+ extract tool tests) |

---

## History / intent

- Earlier mistake: compose “Launch scrape” + listen toggles treated as job queues.
- Correct model: **Scrapers grow the lake; Research drinks from the lake.**
- This pass: rename, kill scrape-from-research, implement listen filters + extract tools over existing signals.
