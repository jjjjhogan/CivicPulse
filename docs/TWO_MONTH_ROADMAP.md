# CivicPulse — 2-month roadmap (pre-alpha → demoable alpha)

**Canonical copy** of the Cursor plan “Two month roadmap.”  
Day-to-day session prompts live in [`SESSION_PLAN.md`](../SESSION_PLAN.md) (not this file).

**Last updated:** 2026-08-19 — New Research compose UI (expansions, listen toggles, extract checkboxes, mock rail) + Weeks 7–8 sessions to persist and launch that configuration.

---

## Capacity reality check

| | |
|--|--|
| **Team** | 2 people × ~3 sessions/week × ~2 hours ≈ **~12 person-hours/week** ≈ **~96 hours / 8 weeks** |
| **Pace rule** | One vertical slice per session. Prefer soak/QA over rushing the next milestone. |
| **Session 1 lesson** | Platform harden + UI polish landed fast; remaining work is heavier (Firebase + Research + **labels**). |

**Foundation today:** Flask `backend/`, **SQLite**, auth/jobs/signals/reports/votes, keyword + Naive Bayes classifier (`scrapers/classifier.py` + `data/labels/labeled_signals.json` ≈ **142** examples), dashboard/map/report UI, TikTok **desktop** scrape.

**Why Firebase before Render:** Render’s filesystem is **ephemeral** — SQLite on disk will not survive deploys. Hosted store = **Firestore** (not Postgres). See [Data platform](#data-platform-sqlite--firebase--render).

**Why classifier work is on the critical path:** Research (“housing prices”) and the mayor demo both **trust categories**. Wrong labels + high % confidence destroy trust. More scrapes without a label loop only multiplies mistakes.

---

## Product north star (week-8 “done”)

A **logged-in mayor-office demo** (Firestore locally; **Render + Firestore** hosted) that:

1. Shows **live DB-backed** signals with **believable** categories (not obviously wrong + fake-high confidence)
2. Lets staff **create a Research** on a topic (e.g. “housing prices”) that:
   - **Searches the archive** (existing signals already ingested)
   - **Pulls new material** via topic-scoped scrape/import jobs
   - Presents a **workspace**: archive vs newly gathered
3. Keeps feed, map, resident reports/votes. The **scrape panel is not on Render** — only a local `is_dev` operator account sees and runs scrapers
4. Produces a **research summary** (topic briefing) for a mayor handout
5. Scraping (including TikTok Selenium) stays on a **dedicated operator machine**, not the hosted site

**Deferred if time slips:** full resolution workflow, citywide daily briefing, map clustering v2, Firebase Auth, hotline, cloud TikTok, vector/embedding search (Phase E only if needed).

```mermaid
flowchart TB
  subgraph quality [Classifier quality loop]
    measure[A Measure gold sample]
    keywords[B Keyword surgery]
    labels[C Label loop]
    uiConf[D Confidence honesty]
    measure --> keywords --> labels
    labels --> uiConf
  end
  subgraph product [Mayor research loop]
    topic[Create Research topic]
    archive[Match existing signals]
    scrape[Queue topic-scoped scrapes]
    workspace[Research workspace UI]
    summary[Topic summary / print]
    topic --> archive --> workspace
    topic --> scrape --> workspace
    workspace --> summary
  end
  subgraph data [Data path]
    sqlite[SQLite local now]
    firestore[Firestore]
    render[Render Flask]
    sqlite --> firestore --> render
  end
  quality --> product
```

---

## Classifier quality loop (phases A–E)

**Current system (do not rewrite first):**

- Keyword pass in `scrapers/categories.py` — one hit often starts confidence ≈ **0.7**
- Naive Bayes in `scrapers/classifier.py` trained on `data/labels/labeled_signals.json` (~**10–14 examples/category**)
- UI **confidence is not calibrated accuracy** — high % next to a wrong category is common when a broad keyword fired

**Strategy:** error-driven labeling + keyword hygiene. **Not** “scrape more and hope.” Architecture upgrades only in Phase E if A–C plateau.

### Phase A — Measure (gold sample)

**Goal:** Know *how* classification fails before changing code.

- Pull a fixed sample of **~50–100** live signals (mix of sources).
- For each: mark **correct / wrong / should-be-none**; note `method` (`keywords`, `model`, `keywords+model`, `inherited`, `outlet_default`) and matched keyword if obvious.
- File results as a simple sheet or `data/labels/review_batch_YYYYMMDD.md` (wrong IDs + notes).
- Summarize top failure modes (e.g. “`noise` too broad”, “housing vs apartment ads”).

**Exit:** Written failure list + gold sample you can re-score after every change.

### Phase B — Keyword surgery (high ROI)

**Goal:** Kill the worst false positives in `CATEGORY_KEYWORDS`.

- Tighten/remove single-token / overly broad terms; prefer multi-word phrases.
- Re-run `python scripts/reprocess_signals.py` (+ import/sync so DB matches).
- Re-score the **same** gold sample; keep a short before/after tally.

**Exit:** Measurable drop in gold-sample false positives; no new model architecture.

### Phase C — Label loop (ongoing)

**Goal:** Grow supervision where the model is weak.

- For wrong cases, add hand-labeled rows to `labeled_signals.json` (true categories **or empty = none**).
- Prefer **hard/error cases** and **negatives**, not more easy “pothole on Culver” clones.
- Target over the 2 months: toward **~30–50 examples per category** + a healthy **none** set (from ~10–14 today).
- After each batch: reprocess → re-check gold sample → commit labels + keyword tweaks together when possible.

**Exit (rolling):** Label count up; gold-sample accuracy trending up; Research archive demos stop looking random.

### Phase D — Confidence honesty (product / UI)

**Goal:** Stop the UI from implying false precision.

- Treat displayed confidence as **match strength**, not “probability correct.”
- Always surface **method** (and inherited/outlet-default clearly).
- Prefer softer copy for keyword-only; optional: hide bare % until calibrated.
- Do **not** invent a new scoring formula until Phase A sample exists.

**Exit:** Demo audience isn’t misled by “92%” on a bad label.

### Phase E — Only if A–C plateau (month 3 default)

- Stronger model / embeddings / vector retrieval — **out of default 2-month scope**.
- Revisit only if gold sample still fails Research demos after solid labels + keywords.

---

## What “Research” means (product contract)

### Mayor story

> “I want to research **housing prices** in Irvine.”  
> CivicPulse creates a Research, scans **what we already have**, kicks off **new** news/social pulls aimed at that topic, and shows one place to read findings.

### Research object (minimum fields)

| Field | Purpose |
|-------|---------|
| `id`, `title` | Display name (“Housing prices — Jul 2026”) |
| `topic` | Free-text topic / question |
| `keywords[]` | Search terms from **suggested expansions** + custom chips |
| `categories[]` | Civic categories inferred from the title / selected expansions |
| `time_window` | Listen window (`7d`, `30d` rolling, `90d`, `ytd`) — **Week 7 persist** |
| `geo_radius` | District / ZIP preset (not a live geofence yet) — **Week 7 persist** |
| `languages[]` | e.g. `en`, `es`, `zh` — **Week 7 persist** |
| `listen_sources[]` | Toggles: twitter, reddit, youtube, tiktok, news311, facebook — **Week 7 persist** |
| `extract[]` | Checkboxes: sentiment, clustering, demographics, policy, misinfo, bots — **Week 7 persist** |
| `status` | `draft` → `gathering` → `ready` → `stale` |
| `created_by`, timestamps | Audit |
| `job_ids[]` | Linked scrape/import jobs |
| `notes` | Optional staff notes (compose UI currently serializes listen config here until Week 7) |

### Two gathering modes

1. **Archive pass** — match existing signals by category overlap + keyword hit in title/body; persist `research_hits`.  
   *Depends on Phase B/C so “housing” isn’t full of sanitation noise.*
2. **New ingest** — topic-scoped news/import/TikTok-desktop jobs; attach matching new signals when jobs sync.

### Workspace UI (v1)

**Compose (`research.html`):** topic prompt, suggested expansions, time/geo/language, listen toggles, extract checkboxes, mock metrics + ethics rail.  
**Workspace (`research-detail.html`):** list / detail / Archive tab / Jobs tab / job status / refresh archive / print summary.

### Out of scope for Research v1

Embeddings, cloud TikTok, multi-city, LLM chat literature review.

---

## Data platform: SQLite → Firebase → Render

| Decision | Choice |
|----------|--------|
| Hosted DB | **Cloud Firestore** |
| App server | **Flask on Render** (gunicorn) |
| Auth (2-month) | **Flask sessions** (Firebase Auth = stretch) |
| Local SQLite | Through Week 2 (+ tests fallback) |
| Postgres | **Not the path** |

**Migration shape:** store interface → Firestore impl (`DATA_BACKEND=firestore`) → export script → cut over local → Render with service-account env → pytest via emulator/mocks.

**Risks:** Firestore ≠ SQL full-text; design archive matching for Firestore constraints in Week 3; never commit service-account JSON.

---

## Progress snapshot

### Shipped — Week 1 Session 1 (2026-07-20)

- [x] SQLite `/api/signals`, runbook, TikTok desktop docs
- [x] Reports + votes APIs, UI polish, pytest for new APIs

### Shipped — New Research compose shell (2026-08-19)

- [x] `research.html` compose layout: topic textarea, expansion pills on title idle, time/geo/language, listen toggles, extract checkboxes
- [x] Right rail: mock live-preview metrics, static ethics gate, template buttons (form-fill only)
- [x] Save draft / Launch scrape still use existing `POST /api/researches` (listen config parked in `notes` until Session 25)

### Open next

- [ ] Week 1 Sessions 2–4: soak, UX harden, **Phase A measure** (+ light test debt)
- [ ] Week 2: **Phases B–D** + Research spike
- [ ] Weeks 3–8: Firebase → Research full → **compose persist/launch** → summary/demo (with ongoing Phase C)

---

## Week-by-week plan (session-grained)

~3 sessions/week. Each: merge + `pytest -q` → one milestone → update this file or `SESSION_PLAN.md`.

### Week 1 — Stabilize + start measuring classification

| Session | Focus | Exit |
|---------|--------|------|
| **1** | Platform harden + UI polish | **Done** |
| **2** | Cold-start soak + smoke checklist | Coworker demos in &lt;15 min from docs |
| **3** | Dashboard empty/loading/error + scrape failures | Graceful failure if API down |
| **4** | **Phase A** gold sample (~50–100) + light test debt | Failure-mode notes + reusable review list |

**Do not start Firebase or Research UI in Week 1.**

### Week 2 — Classifier fix loop + Research spike (SQLite)

| Session | Focus | Exit |
|---------|--------|------|
| **5** | **Phase B** keyword surgery + reprocess; start **Phase D** (method + honest confidence copy) | Gold sample false positives down; UI less misleading |
| **6** | **Phase C** label batch #1 (errors + none) + reprocess | Labels committed; gold sample re-checked |
| **7** | Research model + `POST/GET /api/researches` (SQLite) | Create/list research in API + minimal UI |
| **7.5** | **Phase C #2** hygiene: keyword pass + manual remove/clear bad signals + reprocess + gold re-score | Fewer live FPs; corpus clean enough for archive demos |
| **8** | Archive matcher → `research_hits` + retro (Firestore schema sketch) | “Housing” research mostly sensible hits; Session 9 owner named |

**Week 2 exit:** Classification visibly less embarrassing on the gold sample; mayor can create a research and see **archive** hits that aren’t random. Run **7.5 before 8** so archive matching isn’t flooded with lifestyle/ads FPs.

### Weeks 3–4 — Firebase, then Render (Person B keeps Phase C)

| Session | Focus | Exit |
|---------|--------|------|
| **9** | Firestore project + emulator docs | README: run emulator |
| **10** | Store interface + Firestore `signals` | `/api/signals` with `DATA_BACKEND=firestore` |
| **11** | Port users, jobs, votes, reports | Login/vote/jobs on Firestore |
| **12** | Port researches + hits; SQLite→Firestore export | Research still works |
| **13** | Cut over local demo to Firestore | Cold demo on Firestore |
| **14** | Render + Firebase credentials | Public URL loads login |
| **15** | Seed/import on hosted; **`is_dev` + local-only scraper gate** | Render hides scrapers; local `is_dev` user can run jobs; 403 otherwise |
| **16** | CI + buffer; **Phase C** batch #2 if gold sample still weak | PR checks green |

**Weeks 3–4 exit:** Render + Firestore; Research archive path works; SQLite not required in prod.

### Weeks 5–6 — Research workspace full loop (+ ongoing labels)

| Session | Focus | Exit |
|---------|--------|------|
| **17–18** | Research workspace UI (list/detail, archive/new, status) | Staff drives research without API tools |
| **19–20** | Topic → keyword assist + category picker; **Phase C** batch #3 on research false hits | Creating “housing prices” feels guided |
| **21–22** | Wire news/import jobs to research; auto-attach matching signals | New tab fills after a news job |
| **23–24** | TikTok/desktop job link + operator copy in UI | Pending desktop scrape on local `is_dev` machine; Render never starts jobs |
| **Buffer** | Hit ranking, empty states, refresh archive | 5-minute mayor walkthrough works |

**Weeks 5–6 exit:** Create topic → archive hits → gather → new hits → open signals.

### Weeks 7–8 — Compose productize, summary, demo freeze

**Already on `research.html` (shell, not done):** topic textarea + clarity score; suggested-expansion pills after the title idles/blurs; time / geo / language selectors; where-to-listen **toggles**; extract **checkboxes**; right-rail mock metrics + ethics gate; template buttons that **fill the form only**. Save draft / Launch scrape still POST the old research fields and stash listen config in `notes`.

Finish that contract in sessions **25–28**. Keep summary + freeze in **29–32**. Do **not** build a template CMS or real ethics enforcement.

| Session | Focus | Exit |
|---------|--------|------|
| **25** | Persist compose fields on the Research object (`time_window`, `geo_radius`, `languages`, `listen_sources`, `extract`) — SQLite + Firestore + PATCH/GET. Stop stuffing them into `notes`. | Create/detail round-trip shows the same toggles, selectors, and checkboxes. `pytest` for the new JSON fields. |
| **26** | Suggested expansions as a small API (title → voice chips + civic chips + inferred categories), plus custom chips already in the UI. Client calls the API on title idle instead of a hardcoded extras map. | Typing a housing title yields housing-ish chips; selecting chips writes `keywords[]` + `categories[]`. |
| **27** | Wire **Save draft** vs **Launch scrape**: draft stays on the compose page; launch sets `gathering`, runs archive match, and queues topic-scoped jobs **only for sources that are on** (news/TikTok already exist; twitter/reddit/youtube/facebook stay as “armed but not implemented” with honest UI copy). | Launch lands in the workspace with archive hits and at least one real job path for enabled sources. Disabled Facebook does nothing. |
| **28** | Right rail: replace fake voice counts with estimates from archive size × sources × window; keep **ethics gate as a static reviewed checklist** (no new compliance engine); templates remain form-fill only (no template store). | Metrics change when toggles/window change and cite a real denominator; demo script can point at ethics copy without implying a live audit. |
| **29** | Research **summary** API + print/HTML (uses extract flags: sentiment/clustering/policy in the one-pager; skip sections that were unchecked) | One-pager for that topic; extract checkboxes actually change the briefing |
| **30** | Map filter pins **by active research**; geo selector is still a preset label, not a hard geofence | Geo view of research hits |
| **31** | **Phase D** polish + hardening + operator/demo seed | No “92% wrong” moments; compose → workspace walkthrough is under 5 minutes |
| **32** | Feature freeze + two full demo rehearsals | 10-minute mayor script without chaos |

**Session 25–28 checklist (compose):**

- [x] Expansions regenerate when the title is finished (idle ~600ms or blur) — **client map today; Session 26 = API**
- [x] Dark “voice” chips vs light “civic” chips; `+ add custom` works
- [x] Time window + language + geo preset on the compose form
- [x] Where-to-listen uses toggles; Facebook default off
- [x] Extract options stay **checkboxes** at the bottom of compose
- [x] Metrics rail is labeled estimate; ethics gate is mock/static
- [x] Template buttons prefill title/chips only — **no template CRUD**
- [x] Research model/API stores listen + extract + window/lang/geo (not only `notes`) — **Session 25**
- [x] Launch scrape queues jobs for enabled sources — **Session 27**
- [x] Metrics cite a real archive denominator — **Session 28**

**Phase E** only if gold sample still fails after batches — park for month 3 by default.

**Weeks 7–8 exit:** Mayor can configure a research from the compose screen, launch it, read a topic summary, and demo without fake-precision classifier theater. Known bugs listed. Templates and live ethics audits remain out of scope.

---

## What we are deliberately de-prioritizing

| Earlier idea | Now |
|--------------|-----|
| Render + **Postgres** | **Firestore** |
| Standalone daily city briefing | **Research summary** |
| Resolution + map clusters as Weeks 5–6 hero | Thin map-by-research; resolution optional |
| Firebase Auth weeks 7–8 | Stretch |
| Research **templates as saved objects** | Form-fill chips only (Session 28) |
| Live ethics / PII scanner | Static ethics-gate copy |
| Classifier rewrite / embeddings | **Phase E / month 3** unless blocked |
| Research as month-3-only | Weeks 2–8 |

---

## Role split (suggested)

| Person A (platform) | Person B (product / NLP / research UX) |
|---|---|
| Store interface, Firestore, Render, CI | **Phases A–C** (review, keywords, labels), Phase D copy |
| Jobs ↔ research linking | Research compose UI, archive matcher, summary/print |
| Emulator + secrets docs | Gold sample ownership, demo narrative |

Classifier quality is **Person B–led** but both re-score the gold sample after changes.

---

## Session rhythm

1. **15 min** — merge + `pytest -q` + glance at gold-sample regressions  
2. **80 min** — **one** milestone (platform **or** classifier **or** research — not all three)  
3. **15 min** — commit/PR, tick boxes, name next owner in `SESSION_PLAN.md`

---

## Explicit non-goals (month 3+)

- Hotline / call-transcript ingestion  
- Embedding / vector search (**Phase E** only if forced)  
- Always-on TikTok Selenium in the cloud  
- Scrapers on the Render dashboard (hosted jobs) — operators scrape locally with `is_dev`  
- Multi-tenant / multi-city / native mobile  
- Pure Firebase client rewrite  

---

## Success metrics at week 8

- [ ] Cold demo on **Firestore** (local) and **Render**  
- [ ] **Gold sample** re-scored: clear improvement vs Phase A baseline (track wrong-rate)  
- [ ] Labels file grown meaningfully (directionally toward ~30+/category, not still ~12)  
- [ ] Mayor can **compose a Research** (expansions, window/language, listen toggles, extract checkboxes) and get sensible **archive hits** for a topic like housing  
- [ ] ≥1 **new gather** path attaches signals into that research  
- [ ] Research **summary** printable without hand-editing  
- [ ] Confidence UI shows **method**; demo script doesn’t lean on fake precision  
- [ ] TikTok / scrapers = local `is_dev` operator only; Render never shows or starts jobs  
- [ ] `pytest -q` green (CI if enabled)  

---

## Related docs

| File | Purpose |
|------|---------|
| [`SESSION_PLAN.md`](../SESSION_PLAN.md) | Next-session checklist / coworker prompts |
| [`INTEGRATION.md`](INTEGRATION.md) | API + CLI (`reprocess_signals`) |
| [`TIKTOK_SCRAPE.md`](TIKTOK_SCRAPE.md) | Desktop TikTok |
| [`BACKEND_PLATFORM_HANDOFF.md`](BACKEND_PLATFORM_HANDOFF.md) | Backend status |
| `data/labels/labeled_signals.json` | NB training labels (Phase C) |
| `scrapers/categories.py` / `scrapers/classifier.py` | Keywords + model (Phases B–C) |
| Cursor plan `two_month_roadmap_*.plan.md` | Short mirror — edit **this** file first |
