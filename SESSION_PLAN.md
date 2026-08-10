# CivicPulse — session plan (Real Firebase cutover)

**For:** Coworker / coding agent owning Firebase Console access and the live Firestore project.  
**Goal this session:** Collect the right Firebase credentials and wire `.env` so CivicPulse can run against the **real** Firestore project and migrate signals from SQLite.

**Not** Research product work. **Not** classifier / Path A UI.  
**Canonical setup docs:** [`docs/FIRESTORE_SETUP.md`](docs/FIRESTORE_SETUP.md) · durability: [`docs/DATA_DURABILITY.md`](docs/DATA_DURABILITY.md)

---

## Context (already in the repo)

- App switches storage with `DATA_BACKEND=sqlite|firestore` ([`backend/store.py`](backend/store.py)).
- Real cloud client: [`backend/firestore.py`](backend/firestore.py) — needs **project id** + **service-account JSON path**. There is **no** Postgres-style database URL.
- Signal docs use id = `stable_id`. Seed scripts:
  - `python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson`
  - `python scripts/import_signals_firestore.py -i data/exports/signals.ndjson`
- Emulator is optional only. For the real project, **do not** set `FIRESTORE_EMULATOR_HOST`.
- Research / `research_hits` still use SQLite until a later session — signals, users, votes, jobs are the Firestore cutover target now.
- Never commit service-account JSON (gitignored). Put the file outside the repo or under a private path and point `.env` at it.

---

## Stay off

- Do not paste private keys or full SA JSON into chat, PRs, or `SESSION_PLAN.md`.
- Do not commit `*-firebase-adminsdk*.json` or `.env`.
- Do not wipe SQLite / ponds while validating Firestore — keep SQLite as rollback until smoke passes.
- Do not port Research to Firestore in this session.

---

## What we need from Firebase (checklist)

Hand these to the agent that has Console access (values go in **local `.env` only**):

| Item | Where in Firebase Console | Env var / file |
|------|---------------------------|----------------|
| **Project ID** | Project settings → General (also in console URL: `…/project/<PROJECT_ID>/…`) | `FIREBASE_PROJECT_ID` and `GOOGLE_CLOUD_PROJECT` (same value) |
| **Service-account JSON** | Project settings → Service accounts → *Generate new private key* | Save file privately; set `GOOGLE_APPLICATION_CREDENTIALS` to its **absolute path** |
| **Firestore enabled** | Build → Firestore Database → create DB if missing (**Native** mode) | — |
| **Confirm region** | Shown when creating Firestore (e.g. `nam5` / `us-central`) | Note in PR/description only; not an env var for Admin SDK |
| **`.firebaserc` default** | Same project id | Edit [`.firebaserc`](.firebaserc) `"default"` for CLI index/rules deploy |

Optional later (not blocking seed): Firebase CLI login + `firebase deploy --only firestore:indexes,firestore:rules`.

---

## Agent prompt (copy into coworker agent chat)

```text
Repo: CivicPulse (Ryan/). You own the real Firebase project cutover credentials.

Read SESSION_PLAN.md and docs/FIRESTORE_SETUP.md.

Your job:
1. From Firebase Console, collect ONLY:
   - Project ID (string)
   - A service-account JSON key file saved on disk (never commit it; never paste the private key into chat)
   - Confirm Cloud Firestore is created in Native mode
2. Update local .env (gitignored) with:
   DATA_BACKEND=firestore
   FIREBASE_PROJECT_ID=<project-id>
   GOOGLE_CLOUD_PROJECT=<project-id>
   GOOGLE_APPLICATION_CREDENTIALS=<absolute-path-to-sa.json>
   Do NOT set FIRESTORE_EMULATOR_HOST.
3. Set .firebaserc "default" to the same project id.
4. With SQLite data already healthy, run:
   python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson
   python scripts/import_signals_firestore.py -i data/exports/signals.ndjson
5. Start dashboard_server.py and smoke:
   - GET /api/signals returns storage "firestore" and a non-zero count
   - signup/login, create a report, cast a vote
6. Report back: project id (ok to share), whether seed count matched SQLite active signals, and any errors. Do not share the service-account JSON contents.

Do NOT:
- Commit .env or the SA JSON
- Delete local SQLite / data/pool / data/signals
- Port Research/research_hits to Firestore
- Point at the emulator for this cutover
```

---

## Exit criteria

- [ ] `.env` configured for real project (SA path works; no emulator host)
- [ ] Signals seeded into cloud Firestore (`signals/{stable_id}`)
- [ ] `/api/signals` shows `"storage": "firestore"` with expected count
- [ ] Auth + report + vote smoke OK
- [ ] Coworker confirms project id + seed result (no secrets in chat/PR)

**Roadmap pointer:** Weeks 3–4 cutover in [`docs/TWO_MONTH_ROADMAP.md`](docs/TWO_MONTH_ROADMAP.md) (Sessions 12–14 still cover Research port + Render).
