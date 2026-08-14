# CivicPulse — session plan (Session 15: hosted seed + dev-gated local scrapers)

**Goal:** Keep scraping off the Render mayor dashboard. Only a Firestore `is_dev` account on a local machine can see and run scrapers.

---

## Session 15 — Seed/import on hosted; `is_dev` + local-only scraper gate

### Completed (this branch)

- [x] Feature branch `feature/dev-local-scrapers`
- [x] User field `is_dev` on SQLite (`User` + migration v2) and Firestore `users` docs
- [x] `public_user` / `GET /api/auth/me` include `is_dev`, `scrapers_allowed`, `scrapers_host_ok`
- [x] `GET /api/config` includes `scrapers_available` (false on Render)
- [x] `POST /api/jobs` and legacy scrape start routes return 403 unless local + `is_dev`
- [x] Dashboard hides scraper nav/section on Render; local non-dev sees a locked note
- [x] Docs: [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md), [`docs/FIRESTORE_SETUP.md`](docs/FIRESTORE_SETUP.md)

### Hosted seed (operator)

- [ ] Confirm Render + Firestore has demo signals/users
- [ ] Re-import if the hosted project is empty (`scripts/import_signals_firestore.py`)
- [ ] Smoke-test public URL: login → feed/research; **no scraper panel**
- [ ] Promote operator: Firebase Console → `users` → set `is_dev: true`
- [ ] Localhost as that account: scraper panel visible; jobs can start

### Visibility rule

```
scrapers_allowed = (not on Render) AND (current_user.is_dev == true)
```

Promote to dev is **manual only** (no admin UI/script this session).

### Notes

- TikTok still needs desktop Chrome; Render never starts scrape jobs (403)
- Mayor demo accounts stay `is_dev: false` so they never see the scrape panel

---

## Exit criteria

- [x] Render / `RENDER=1`: jobs API 403; UI hides scrapers
- [x] Local + `is_dev` false: jobs API 403
- [x] Local + `is_dev` true: jobs can start
- [ ] Hosted seed verified on the live Render URL
- [ ] `pytest -q` green

---

## Next: Session 16 — CI + buffer; Phase C batch #2 if gold sample still weak

Per [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md).
