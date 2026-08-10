# Firestore setup (local emulator)

CivicPulse can run against **Cloud Firestore** instead of SQLite.
For local development, use the Firebase Emulator Suite — no Google
Cloud project or credentials required.

## Prerequisites

1. **Node.js** (v18+) — [nodejs.org](https://nodejs.org/)
2. **Java** (JDK 11+) — required by the Firestore emulator
3. **Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```
4. **firebase-admin** Python package (already in `requirements.txt`):
   ```bash
   pip install firebase-admin
   ```

## Start the emulator

From the project root (where `firebase.json` lives):

```bash
firebase emulators:start --only firestore
```

This starts:
- Firestore emulator on `127.0.0.1:8081`
- Emulator UI on `http://localhost:4000` (browse collections, run queries)

The emulator automatically sets `FIRESTORE_EMULATOR_HOST` for child
processes. For the Flask server running in a separate terminal, set it
manually:

```bash
# Linux/macOS
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8081

# Windows PowerShell
$env:FIRESTORE_EMULATOR_HOST = "127.0.0.1:8081"
```

## Run CivicPulse with Firestore

```bash
# Terminal 1 — emulator
firebase emulators:start --only firestore

# Terminal 2 — Flask server
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8081
export DATA_BACKEND=firestore
python scripts/dashboard_server.py
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_BACKEND` | `sqlite` | `sqlite` or `firestore` |
| `FIRESTORE_EMULATOR_HOST` | *(unset)* | Set to `127.0.0.1:8081` for local emulator |
| `GOOGLE_CLOUD_PROJECT` | `civicpulse-local` | Project ID (emulator accepts any value) |
| `GOOGLE_APPLICATION_CREDENTIALS` | *(unset)* | Path to service-account JSON (prod only) |

## Firestore collections

| Collection | SQLite equivalent | Key fields |
|------------|-------------------|------------|
| `signals` | `signals` table | source, title, body, url, categories, published_utc, metadata |
| `users` | `users` table | email, name, password_hash |
| `scrape_jobs` | `scrape_jobs` table | source, status, settings, log |
| `issue_votes` | `issue_votes` table | signal_id, user_id, choice |
| `researches` | `researches` table | title, topic, keywords, categories, status |
| `research_hits` | `research_hits` table | research_id, signal_id, match_reason, score |

## Running tests against Firestore

```bash
export FIRESTORE_EMULATOR_HOST=127.0.0.1:8081
export DATA_BACKEND=firestore
py -m pytest -q
```

Tests use the emulator and clear collections between runs.
The default (`DATA_BACKEND=sqlite`) uses in-memory SQLite as before.

## Production (Render)

On Render, set `DATA_BACKEND=firestore` and point
`GOOGLE_APPLICATION_CREDENTIALS` to the service-account JSON (stored
as a Render secret file). Do **not** commit service-account JSON.
