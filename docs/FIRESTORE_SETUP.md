# Firestore / Firebase (real project + optional emulator)

CivicPulse switches storage with `DATA_BACKEND=firestore`.
The Admin SDK talks to **your Firebase project** (or a local emulator).
There is **no database URL** like Postgres — you need a **Project ID** and a
**service-account JSON**.

Store layout: [`backend/store.py`](../backend/store.py),
[`backend/store_sqlite.py`](../backend/store_sqlite.py),
[`backend/store_firestore.py`](../backend/store_firestore.py).

## What to get from Firebase Console

1. **Project ID** — Project settings → General (also in the console URL:
   `https://console.firebase.google.com/project/<PROJECT_ID>/...`).
2. **Service account JSON** — Project settings → Service accounts →
   *Generate new private key*. Save outside the repo (or under a gitignored path).
3. Enable **Cloud Firestore** in the console (Native mode).

Put values in `.env` (see [`.env.example`](../.env.example)):

```env
DATA_BACKEND=firestore
FIREBASE_PROJECT_ID=your-firebase-project-id
GOOGLE_CLOUD_PROJECT=your-firebase-project-id
GOOGLE_APPLICATION_CREDENTIALS=C:/secure/path/civicpulse-sa.json
```

**Unset** `FIRESTORE_EMULATOR_HOST` when targeting the real project.

Also set `"default"` in [`.firebaserc`](../.firebaserc) to the same project id
(for CLI deploy of rules/indexes).

## Migrate SQLite signals → real Firestore

Keep ponds/signals healthy on SQLite first ([`DATA_DURABILITY.md`](DATA_DURABILITY.md)).

```powershell
# .env already points at the real project (no emulator host)
$env:DATA_BACKEND = "firestore"
# or rely on .env loaded by the app

python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson
python scripts/import_signals_firestore.py -i data/exports/signals.ndjson
python scripts/dashboard_server.py
```

Doc id = **`stable_id`**. Soft-archived rows are omitted from default list APIs.

**Still on SQLite until Session 12:** Research / `research_hits`.
Signals, users, votes, and scrape jobs use Firestore after seed.

Deploy indexes/rules (once CLI is logged into the project):

```bash
firebase deploy --only firestore:indexes,firestore:rules
```

## Environment variables

| Variable | Required for real project | Description |
|----------|---------------------------|-------------|
| `DATA_BACKEND` | `firestore` | Backend switch |
| `FIREBASE_PROJECT_ID` | yes | Firebase project id |
| `GOOGLE_CLOUD_PROJECT` | recommended (same id) | Alias used by Google libs |
| `GOOGLE_APPLICATION_CREDENTIALS` | yes | Absolute path to SA JSON |
| `FIRESTORE_EMULATOR_HOST` | must be **unset** | Only for local emulator |

## Firestore collections

| Collection | Doc id | Key fields |
|------------|--------|------------|
| `signals` | `stable_id` | source, outlet, title, body, url, categories, published_utc, metadata, archived_at, timestamps, ingest_job_id |
| `users` | auto | email, name, password_hash |
| `scrape_jobs` | auto | source, status, settings, log |
| `issue_votes` | `{signal_id}_{user_id}` | signal_id, user_id, choice |
| `researches` / `research_hits` | *(not ported)* | still SQLite |

Indexes: [`firestore.indexes.json`](../firestore.indexes.json).

## Smoke checklist (real project)

1. `GET /api/signals` → `"storage": "firestore"`, expected count after seed
2. Signup / login
3. Create report + vote
4. Create scrape job (post-scrape sync upserts into Firestore)
5. Confirm docs in Firebase Console → Firestore

## Optional: local emulator

For offline work without cloud credentials:

```bash
firebase emulators:start --only firestore
# FIRESTORE_EMULATOR_HOST=127.0.0.1:8081
# DATA_BACKEND=firestore
```

## Production (Render)

Same env vars: `DATA_BACKEND=firestore`, project id, and
`GOOGLE_APPLICATION_CREDENTIALS` pointing at a Render **secret file**.
Never commit the service-account JSON.

## Tests

```bash
pytest -q
```

Default suite uses SQLite + mocked Firestore (no cloud call).
