# CivicPulse — session plan (Sessions 19–20: Topic keyword assist + category picker)

**Goal:** Make research creation and editing feel guided — category picker with clickable buttons, keyword suggestions from curated lists.

---

## Sessions 19–20 — Topic keyword assist + category picker

### Completed

**Backend:**
- [x] `/api/config` returns `category_keywords` — curated suggestions per category from `DEFAULT_SEARCH_TERMS`

**Research create form (`research.html` + `research.js`):**
- [x] Category picker — clickable toggle buttons replace free-text categories input
- [x] Keyword suggestions — chips appear when categories are selected, clicking appends to keyword input
- [x] Suggestions filtered against already-entered keywords
- [x] Chips removed after clicking, section hides when no suggestions remain
- [x] Form reset clears picker state and suggestions

**Research detail workspace (`research-detail.js`):**
- [x] Fetches `/api/config` on load for categories + keyword suggestions
- [x] Category edit uses picker buttons instead of CSV text input
- [x] Pre-selects current research categories when entering edit mode
- [x] Keyword suggestions appear during category edit based on selected categories
- [x] Clicking suggestion chips appends keywords to the keyword input
- [x] Cancel resets picker and hides suggestions

**CSS (`research.css`):**
- [x] `.cat-picker`, `.cat-pick-btn`, `.cat-pick-btn.selected` — toggle button styles
- [x] `.kw-suggestions`, `.kw-chips`, `.kw-chip` — suggestion chip styles
- [x] `.detail-value-col`, `.inline-actions`, `.inline-row` — detail page edit layout

**Tests:**
- [x] All 136 tests pass (no new tests needed — existing PATCH/DELETE tests cover the API)

### Modified files

| File | Change |
|------|--------|
| `backend/routes/signals.py` | Added `category_keywords` to `/api/config` response |
| `research.html` | Category picker div + keyword suggestions area in create form |
| `research.js` | Category picker + keyword assist logic in create flow |
| `research-detail.js` | Config loading, category picker in edit mode, keyword suggestions |
| `research.css` | Category picker, keyword chip, detail edit layout styles |

### Browser verification

- [x] Create form: 10 category buttons rendered from `/api/config`
- [x] Create form: selecting categories shows keyword suggestion chips
- [x] Detail page: Edit categories shows picker with current categories pre-selected
- [x] Detail page: keyword suggestions appear (e.g. "car crash", "hit and run" for traffic_safety)
- [x] Detail page: clicking chip appends keyword to input, chip removed
- [x] Detail page: Cancel resets edit state and hides suggestions
- [x] No console errors

---

## Exit criteria

- [x] `/api/config` serves `category_keywords` from `DEFAULT_SEARCH_TERMS`
- [x] Create form uses clickable category picker instead of text input
- [x] Keyword suggestions appear based on selected categories
- [x] Detail page inline edit uses same picker pattern
- [x] 136 tests pass
- [x] Browser verification — picker and suggestions working in both create and edit flows

---

## Previous sessions

- **Sessions 17–18** — Research workspace UI (PATCH/DELETE, tabs, inline edit, filters)
- **Session 16** — GitHub Actions CI workflow
- **Session 15** — Desktop-only Selenium messaging
- **Session 14** — Render deployment config
- **Session 13** — Cold demo end-to-end on Firestore
- **Session 12** — Research store (SQLite + Firestore)
- **Session 11** — Port users, jobs, votes, reports to Firestore

---

## Next: Sessions 21–22 — Phase C batch #3 + research-scoped jobs

Per [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md): Phase C label batch #3 to improve classifier accuracy; link scrape jobs to research topics so the "New" tab populates.
