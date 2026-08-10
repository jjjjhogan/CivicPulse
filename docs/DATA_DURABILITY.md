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

## Firestore cutover checklist (later)

1. Run emulator; set `FIRESTORE_EMULATOR_HOST`.
2. `python scripts/export_signals_ndjson.py -o data/exports/signals.ndjson`.
3. Bulk-load NDJSON into Firestore (`signals/{stable_id}`).
4. Flip `DATA_BACKEND=firestore` locally; compare counts vs SQLite.
5. Optional: export ponds → NDJSON → `raw_items/{stable_id}` (not required for Sessions 9–10).
6. Render: service-account secret; never commit SA JSON.
7. Disable SQLite in prod after smoke checks.

See also [`TWO_MONTH_ROADMAP.md`](TWO_MONTH_ROADMAP.md) Sessions 9–14.
