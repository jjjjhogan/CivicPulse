# Path B — Data durability

## Model

| Layer | Role | Location |
|-------|------|----------|
| **Giant pool / ponds** | Cumulative scraped corpus (pre-filter). Merge by `stable_id`; never shrink on scrape/reprocess. | `data/pool/{tiktok,reddit,twitter,news}.json` |
| **Signal pool** | Derived civic subset after keywords/NLP. Regenerable from ponds. | `data/signals/{source}.json` |
| **SQLite `signals`** | API source of truth (active rows). | `data/civicpulse.db` |
| **Job raw** (optional) | Per-run debug artifact; merge into pond. | `data/raw/…` |
| **Backups** | Timestamped full SQLite copies before destructive ops. | `data/backups/civicpulse_YYYYMMDD_HHMMSS.db` |

```text
Scrape → merge pond → classify → signals JSON → upsert SQLite → /api/signals
```

Keyword/NLP changes: re-read ponds → rewrite signals → upsert DB (no re-scrape). Legacy `*_all.json` is absorbed into ponds via bootstrap.

## Policies

- **`stable_id`:** SHA-256 hex of `source + "\n" + normalized_url + "\n" + fragment`, truncated to 40 chars. Fragment prefers platform ids (`post_id`, `comment_id`, …) else a body fingerprint (so TikTok comments sharing a video URL stay distinct, while title truncation does not churn ids). Same id in pond, signal JSON, and SQLite.
- **Delete:** default reprocess = rewrite signals + upsert only. `--archive-missing` soft-hides DB rows (backup first). `--prune` hard-deletes (backup required). Scope to processed sources only. Ponds never auto-deleted.
- **API:** SQLite only (`archived_at IS NULL`). JSON fallback if table empty. Response keys unchanged for Path A.
- **Bootstrap:** `python scripts/bootstrap_pool.py` seeds ponds from `signals/*`, `*_all.json`, and raw if present.

## Operator runbook

1. **Scrape / process** — merges into `data/pool/{source}.json`, derives `data/signals/{source}.json`, upserts SQLite.
2. **Reprocess after keyword changes** — `python scripts/reprocess_signals.py` (reads ponds by default).
3. **Verify counts** — `python scripts/verify_signal_counts.py` (expect pond ≥ signals ≥ active DB per source).
4. **Backup before destructive ops** — automatic when using `--archive-missing`, `--prune`, or `import_signals.py --replace`. Manual: `python -c "from backend.db_backup import backup_database; print(backup_database())"`.
5. **Optional cleanup** — `python scripts/reprocess_signals.py --archive-missing` or `--prune` (scoped to `--source` if set).
6. **Restore drill** — `python scripts/restore_db.py --from data/backups/civicpulse_….db --force` (point `DATABASE_URL` at a side copy first when practicing).

Tests use a temp SQLite via `DATABASE_URL` and never touch `data/civicpulse.db`.

## Firestore cutover checklist (real Firebase project)

Full steps: [`FIRESTORE_SETUP.md`](FIRESTORE_SETUP.md).

Firebase is **not** a connection URL. You need **Project ID** + **service-account JSON**.

1. SQLite healthy: ponds + signals + migrate/import/reprocess.
2. Put in `.env`: `DATA_BACKEND=firestore`, `FIREBASE_PROJECT_ID=…`, `GOOGLE_APPLICATION_CREDENTIALS=…`.
3. `python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson`
4. `python scripts/import_signals_firestore.py -i data/exports/signals.ndjson` → cloud docs at `signals/{stable_id}`
5. Smoke `/api/signals`, auth, votes, jobs. Research stays on SQLite until Session 12.
6. `firebase deploy --only firestore:indexes,firestore:rules` when ready.
7. Render: same env + SA secret file; never commit SA JSON.

Store switch: `backend/store.py` → sqlite or firestore impl. Path B ponds remain local JSON.


