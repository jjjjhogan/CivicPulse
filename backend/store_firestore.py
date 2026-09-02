"""Firestore stores."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from google.api_core.exceptions import FailedPrecondition

from backend.paging import decode_cursor, encode_cursor
from backend.stable_id import compute_stable_id, ensure_stable_id


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

def _doc_to_signal_dict(doc) -> dict:
    data = doc.to_dict() or {}
    return {
        "id": doc.id,
        "stable_id": data.get("stable_id") or doc.id,
        "source": data.get("source", ""),
        "outlet": data.get("outlet", ""),
        "title": data.get("title", ""),
        "body": data.get("body", ""),
        "url": data.get("url", ""),
        "categories": data.get("categories", []),
        "published_utc": data.get("published_utc", ""),
        "metadata": data.get("metadata", {}),
    }


def _doc_to_feed_dict(doc) -> dict:
    data = doc.to_dict() or {}
    return {
        "outlet": data.get("outlet", ""),
        "title": data.get("title", ""),
        "categories": data.get("categories", []),
        "published_utc": data.get("published_utc", ""),
    }


def _is_archived(data: dict) -> bool:
    return bool(data.get("archived_at"))


class FirestoreSignalStore:
    COLLECTION = "signals"

    def __init__(self, db) -> None:
        self._db = db

    def _coll(self):
        return self._db.collection(self.COLLECTION)

    def _filter_archived(self, docs, *, include_archived: bool) -> list:
        out = []
        for doc in docs:
            data = doc.to_dict() or {}
            if include_archived or not _is_archived(data):
                out.append(doc)
        return out

    def _signals_query(
        self,
        *,
        include_archived: bool = False,
        source: str | None = None,
        category: str | None = None,
    ):
        query = self._coll()
        if not include_archived:
            query = query.where("active", "==", True)
        if source:
            query = query.where("source", "==", source)
        if category:
            query = query.where("categories", "array_contains", category)
        return query.order_by("created_at", direction="DESCENDING")

    def _legacy_signals_query(
        self,
        *,
        source: str | None = None,
        category: str | None = None,
    ):
        """Pre-index fallback: filter archived client-side via archived_at."""
        query = self._coll()
        if source:
            query = query.where("source", "==", source)
        if category:
            query = query.where("categories", "array_contains", category)
        # Equality filters + order_by need composite indexes; sort client-side instead.
        if not source and not category:
            return query.order_by("created_at", direction="DESCENDING")
        return query

    @staticmethod
    def _sort_docs_newest(docs: list) -> list:
        return sorted(
            docs,
            key=lambda d: (d.to_dict() or {}).get("created_at", ""),
            reverse=True,
        )

    def _stream_docs(self, query, *, include_archived: bool) -> list:
        docs = list(query.stream())
        return self._filter_archived(docs, include_archived=include_archived)

    def _stream_signal_docs(
        self,
        *,
        include_archived: bool = False,
        source: str | None = None,
        category: str | None = None,
        limit: int | None = None,
        offset: int = 0,
        cursor: str | None = None,
    ) -> list:
        """Run indexed query; fall back when composite indexes are not deployed yet."""
        fetch_n = None
        if limit is not None:
            fetch_n = max(1, limit) + 1
            if offset and not cursor:
                fetch_n = max(0, offset) + fetch_n
            if not include_archived:
                fetch_n = min(fetch_n * 2, fetch_n + 200)

        def _apply_paging(query):
            if cursor:
                created_at, _doc_id = decode_cursor(cursor)
                query = query.start_after(created_at)
            if fetch_n is not None:
                query = query.limit(fetch_n)
            return query

        try:
            query = _apply_paging(
                self._signals_query(
                    include_archived=include_archived,
                    source=source,
                    category=category,
                )
            )
            return self._stream_docs(query, include_archived=include_archived)
        except FailedPrecondition:
            query = _apply_paging(
                self._legacy_signals_query(source=source, category=category)
            )
            docs = self._stream_docs(query, include_archived=include_archived)
            docs = self._sort_docs_newest(docs)
            if cursor:
                created_at, doc_id = decode_cursor(cursor)
                trimmed = []
                for doc in docs:
                    data = doc.to_dict() or {}
                    doc_created = str(data.get("created_at", ""))
                    if doc_created < created_at:
                        trimmed.append(doc)
                    elif doc_created == created_at and str(doc.id) < doc_id:
                        trimmed.append(doc)
                docs = trimmed
            if offset and not cursor:
                docs = docs[offset:]
            return docs

    def list_signals(
        self,
        *,
        include_archived: bool = False,
        limit: int | None = None,
        offset: int = 0,
        cursor: str | None = None,
        source: str | None = None,
        category: str | None = None,
    ) -> dict:
        docs = self._stream_signal_docs(
            include_archived=include_archived,
            source=source,
            category=category,
            limit=limit,
            offset=offset,
            cursor=cursor,
        )
        next_cursor = None
        if limit is not None and len(docs) > limit:
            docs = docs[:limit]
            last = docs[-1]
            data = last.to_dict() or {}
            next_cursor = encode_cursor(data.get("created_at", ""), last.id)
        elif limit is not None:
            docs = docs[:limit]
        return {
            "signals": [_doc_to_signal_dict(doc) for doc in docs],
            "next_cursor": next_cursor,
        }

    def list_feed_signals(
        self,
        *,
        include_archived: bool = False,
        limit: int | None = None,
        offset: int = 0,
        cursor: str | None = None,
        source: str | None = None,
        category: str | None = None,
    ) -> dict:
        page = self.list_signals(
            include_archived=include_archived,
            limit=limit,
            offset=offset,
            cursor=cursor,
            source=source,
            category=category,
        )
        return {
            "signals": [
                {
                    "outlet": row.get("outlet", ""),
                    "title": row.get("title", ""),
                    "categories": row.get("categories") or [],
                    "published_utc": row.get("published_utc", ""),
                }
                for row in page["signals"]
            ],
            "next_cursor": page["next_cursor"],
        }

    def count_signals(
        self,
        *,
        sources: list[str] | None = None,
        include_archived: bool = False,
        source: str | None = None,
        category: str | None = None,
    ) -> int:
        """Cheap-ish count via aggregation when possible; falls back to streaming."""
        if sources:
            total = 0
            for src in sources:
                total += self._count_signals_with_fallback(
                    include_archived=include_archived, source=src, category=category,
                )
            return total
        return self._count_signals_with_fallback(
            include_archived=include_archived, source=source, category=category,
        )

    def _count_query(self, query, *, include_archived: bool) -> int:
        try:
            aggregation = query.count().get()
            value = 0
            for result in aggregation:
                value = int(result[0].value)
                break
            return value
        except FailedPrecondition:
            raise
        except Exception:  # noqa: BLE001
            docs = list(query.stream())
            docs = self._filter_archived(docs, include_archived=include_archived)
            return len(docs)

    def _count_signals_with_fallback(
        self,
        *,
        include_archived: bool = False,
        source: str | None = None,
        category: str | None = None,
    ) -> int:
        try:
            return self._count_query(
                self._signals_query(
                    include_archived=include_archived, source=source, category=category,
                ),
                include_archived=include_archived,
            )
        except FailedPrecondition:
            return self._count_query(
                self._legacy_signals_query(source=source, category=category),
                include_archived=include_archived,
            )

    def get_signal(self, signal_id: int | str) -> dict | None:
        doc = self._coll().document(str(signal_id)).get()
        if not doc.exists:
            return None
        return _doc_to_signal_dict(doc)

    def create_signal(self, **fields: Any) -> dict:
        metadata = fields.get("metadata") or {}
        if not isinstance(metadata, dict):
            metadata = {}
        source = fields.get("source", "")
        title = fields.get("title", "")
        body = fields.get("body", "")
        url = fields.get("url", "")
        stable_id = (fields.get("stable_id") or "").strip()
        if not stable_id:
            stable_id = compute_stable_id(source, url, title, body, metadata=metadata)
        metadata = {**metadata, "stable_id": stable_id}
        now = _utcnow_iso()
        data = {
            "stable_id": stable_id,
            "source": source,
            "outlet": fields.get("outlet", ""),
            "title": title,
            "body": body,
            "url": url,
            "categories": fields.get("categories", []),
            "published_utc": fields.get("published_utc", ""),
            "metadata": metadata,
            "created_at": now,
            "updated_at": now,
            "last_seen_at": now,
            "archived_at": None,
            "active": True,
            "ingest_job_id": fields.get("ingest_job_id"),
        }
        self._coll().document(stable_id).set(data, merge=True)
        return {
            "id": stable_id,
            "stable_id": stable_id,
            "source": data["source"],
            "outlet": data["outlet"],
            "title": data["title"],
            "body": data["body"],
            "url": data["url"],
            "categories": data["categories"],
            "published_utc": data["published_utc"],
            "metadata": metadata,
        }

    def list_signals_by_source(
        self, source: str, *, include_archived: bool = False, limit: int | None = None,
    ) -> list[dict]:
        try:
            query = self._signals_query(include_archived=include_archived, source=source)
            if limit is not None:
                query = query.limit(limit)
            docs = self._stream_docs(query, include_archived=include_archived)
        except FailedPrecondition:
            query = self._legacy_signals_query(source=source)
            fetch_n = limit
            if limit is not None and not include_archived:
                fetch_n = min(limit * 3, limit + 50)
            if fetch_n is not None:
                query = query.limit(fetch_n)
            docs = self._stream_docs(query, include_archived=include_archived)
            docs = self._sort_docs_newest(docs)
            if limit is not None:
                docs = docs[:limit]
        return [_doc_to_signal_dict(doc) for doc in docs]

    def upsert_many(
        self, rows: list[dict], *, ingest_job_id: int | None = None,
    ) -> dict:
        inserted = 0
        updated = 0
        now = _utcnow_iso()
        batch = self._db.batch()
        ops = 0
        for row in rows:
            if not isinstance(row, dict):
                continue
            if not (row.get("source") or "").strip():
                continue
            ensure_stable_id(row)
            stable_id = row["stable_id"]
            ref = self._coll().document(stable_id)
            existing = ref.get()
            metadata = row.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}
            metadata = {**metadata, "stable_id": stable_id}
            data = {
                "stable_id": stable_id,
                "source": row.get("source") or "",
                "outlet": row.get("outlet") or "",
                "title": row.get("title") or "",
                "body": row.get("body") or "",
                "url": row.get("url") or "",
                "categories": row.get("categories") or [],
                "published_utc": row.get("published_utc") or "",
                "metadata": metadata,
                "updated_at": now,
                "last_seen_at": now,
                "archived_at": None,
                "active": True,
            }
            if ingest_job_id is not None:
                data["ingest_job_id"] = ingest_job_id
            if existing.exists:
                updated += 1
                if not (existing.to_dict() or {}).get("created_at"):
                    data["created_at"] = now
            else:
                inserted += 1
                data["created_at"] = now
            batch.set(ref, data, merge=True)
            ops += 1
            if ops >= 400:
                batch.commit()
                batch = self._db.batch()
                ops = 0
        if ops:
            batch.commit()
        return {"inserted": inserted, "updated": updated}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class FirestoreUserStore:
    COLLECTION = "users"

    def __init__(self, db) -> None:
        self._db = db

    def _coll(self):
        return self._db.collection(self.COLLECTION)

    @staticmethod
    def _to_dict(doc) -> dict:
        data = doc.to_dict()
        return {
            "id": doc.id,
            "email": data.get("email", ""),
            "name": data.get("name", ""),
            "password_hash": data.get("password_hash", ""),
            "is_dev": bool(data.get("is_dev", False)),
        }

    def get_user(self, user_id: int | str) -> dict | None:
        doc = self._coll().document(str(user_id)).get()
        if not doc.exists:
            return None
        return self._to_dict(doc)

    def get_user_by_email(self, email: str) -> dict | None:
        docs = list(self._coll().where("email", "==", email).limit(1).stream())
        if not docs:
            return None
        return self._to_dict(docs[0])

    def create_user(self, *, name: str, email: str, password_hash: str) -> dict:
        data = {
            "email": email,
            "name": name,
            "password_hash": password_hash,
            "is_dev": False,
            "created_at": _utcnow_iso(),
        }
        _, doc_ref = self._coll().add(data)
        return {**data, "id": doc_ref.id}


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class FirestoreJobStore:
    COLLECTION = "scrape_jobs"

    def __init__(self, db) -> None:
        self._db = db

    def _coll(self):
        return self._db.collection(self.COLLECTION)

    @staticmethod
    def _to_dict(doc) -> dict:
        data = doc.to_dict()
        return {
            "id": doc.id,
            "source": data.get("source", ""),
            "status": data.get("status", "pending"),
            "settings": data.get("settings", {}),
            "command": data.get("command"),
            "log": data.get("log", ""),
            "error": data.get("error"),
            "exit_code": data.get("exit_code"),
            "user_id": data.get("user_id"),
            "research_id": data.get("research_id"),
            "created_at": data.get("created_at"),
            "started_at": data.get("started_at"),
            "finished_at": data.get("finished_at"),
        }

    def create_job(self, *, source: str, settings: dict, user_id: Any = None, research_id: Any = None) -> dict:
        data = {
            "source": source,
            "status": "pending",
            "settings": settings or {},
            "command": None,
            "log": "",
            "error": None,
            "exit_code": None,
            "user_id": str(user_id) if user_id else None,
            "research_id": str(research_id) if research_id else None,
            "created_at": _utcnow_iso(),
            "started_at": None,
            "finished_at": None,
        }
        _, doc_ref = self._coll().add(data)
        return {**data, "id": doc_ref.id}

    def get_job(self, job_id: int | str) -> dict | None:
        doc = self._coll().document(str(job_id)).get()
        if not doc.exists:
            return None
        return self._to_dict(doc)

    def list_jobs(self, *, limit: int = 20) -> list[dict]:
        docs = (
            self._coll()
            .order_by("created_at", direction="DESCENDING")
            .limit(limit)
            .stream()
        )
        return [self._to_dict(doc) for doc in docs]

    def update_job(self, job_id: int | str, **fields: Any) -> None:
        update = {}
        for k, v in fields.items():
            if k in ("started_at", "finished_at") and v is not None:
                update[k] = v.isoformat() if hasattr(v, "isoformat") else v
            else:
                update[k] = v
        self._coll().document(str(job_id)).update(update)

    def get_running_job(self) -> dict | None:
        docs = list(
            self._coll()
            .where("status", "==", "running")
            .stream()
        )
        if not docs:
            return None
        docs.sort(
            key=lambda d: (d.to_dict() or {}).get("created_at", ""),
            reverse=True,
        )
        return self._to_dict(docs[0])

    def get_latest_job(self) -> dict | None:
        docs = list(
            self._coll()
            .order_by("created_at", direction="DESCENDING")
            .limit(1)
            .stream()
        )
        return self._to_dict(docs[0]) if docs else None

    def list_jobs_for_research(self, research_id: int | str) -> list[dict]:
        docs = list(
            self._coll()
            .where("research_id", "==", str(research_id))
            .stream()
        )
        docs.sort(
            key=lambda d: (d.to_dict() or {}).get("created_at", ""),
            reverse=True,
        )
        return [self._to_dict(doc) for doc in docs]


# ---------------------------------------------------------------------------
# Votes
# ---------------------------------------------------------------------------

class FirestoreVoteStore:
    COLLECTION = "issue_votes"

    def __init__(self, db) -> None:
        self._db = db

    def _coll(self):
        return self._db.collection(self.COLLECTION)

    @staticmethod
    def _vote_doc_id(signal_id: Any, user_id: Any) -> str:
        return f"{signal_id}_{user_id}"

    def summarize_votes(
        self, signal_ids: list, *, user_id: Any = None,
    ) -> dict[str, dict]:
        result: dict[str, dict] = {
            str(sid): {"up": 0, "down": 0, "mine": None} for sid in signal_ids
        }
        if not signal_ids:
            return result
        str_ids = [str(sid) for sid in signal_ids]
        id_set = set(str_ids)

        def _apply_doc(doc) -> None:
            data = doc.to_dict() or {}
            sid = str(data.get("signal_id", ""))
            if sid not in result:
                return
            choice = data.get("choice", "")
            if choice in {"up", "down"}:
                result[sid][choice] += 1
            if user_id is not None and str(data.get("user_id", "")) == str(user_id):
                result[sid]["mine"] = choice

        batch_size = 30
        try:
            for i in range(0, len(str_ids), batch_size):
                chunk = str_ids[i : i + batch_size]
                docs = self._coll().where("signal_id", "in", chunk).stream()
                for doc in docs:
                    _apply_doc(doc)
        except FailedPrecondition:
            for doc in self._coll().stream():
                data = doc.to_dict() or {}
                if str(data.get("signal_id", "")) in id_set:
                    _apply_doc(doc)
        return result

    def cast_vote(self, *, signal_id: Any, user_id: Any, choice: str) -> None:
        doc_id = self._vote_doc_id(signal_id, user_id)
        doc_ref = self._coll().document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            existing_choice = doc.to_dict().get("choice", "")
            if existing_choice == choice:
                doc_ref.delete()
            else:
                doc_ref.update({"choice": choice, "updated_at": _utcnow_iso()})
        else:
            doc_ref.set({
                "signal_id": str(signal_id),
                "user_id": str(user_id),
                "choice": choice,
                "created_at": _utcnow_iso(),
                "updated_at": _utcnow_iso(),
            })


# ---------------------------------------------------------------------------
# Researches
# ---------------------------------------------------------------------------

class FirestoreResearchStore:
    COLLECTION = "researches"

    def __init__(self, db) -> None:
        self._db = db

    def _coll(self):
        return self._db.collection(self.COLLECTION)

    def _hits_coll(self, research_id: str):
        return self._coll().document(research_id).collection("hits")

    @staticmethod
    def _to_dict(doc) -> dict:
        data = doc.to_dict() or {}
        return {
            "id": doc.id,
            "title": data.get("title", ""),
            "topic": data.get("topic", ""),
            "keywords": data.get("keywords", []),
            "categories": data.get("categories", []),
            "extract": data.get("extract", []),
            "listen_sources": data.get("listen_sources", []),
            "languages": data.get("languages", []),
            "time_window": data.get("time_window", "30d"),
            "geo_radius": data.get("geo_radius", "irvine"),
            "status": data.get("status", "draft"),
            "notes": data.get("notes", ""),
            "created_at": data.get("created_at"),
            "updated_at": data.get("updated_at"),
        }

    def create_research(
        self, *, title: str, topic: str = "", keywords: list | None = None,
        categories: list | None = None, extract: list | None = None,
        listen_sources: list | None = None, languages: list | None = None,
        time_window: str = "30d", geo_radius: str = "irvine",
        notes: str = "",
    ) -> dict:
        now = _utcnow_iso()
        data = {
            "title": title,
            "topic": topic,
            "keywords": keywords or [],
            "categories": categories or [],
            "extract": extract or [],
            "listen_sources": listen_sources or [],
            "languages": languages or [],
            "time_window": time_window,
            "geo_radius": geo_radius,
            "status": "draft",
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }
        _, doc_ref = self._coll().add(data)
        return {**data, "id": doc_ref.id}

    def list_researches(self) -> list[dict]:
        docs = list(self._coll().order_by("created_at", direction="DESCENDING").stream())
        return [self._to_dict(doc) for doc in docs]

    def get_research(self, research_id: int | str) -> dict | None:
        doc = self._coll().document(str(research_id)).get()
        if not doc.exists:
            return None
        return self._to_dict(doc)

    @staticmethod
    def _hit_payload(h: dict, *, now: str) -> dict:
        signal = h.get("signal")
        if not isinstance(signal, dict):
            signal = None
        return {
            "signal_id": str(h["signal_id"]),
            "match_reason": h.get("match_reason", ""),
            "score": h.get("score", 0.0),
            "signal": signal,
            "created_at": now,
        }

    def get_research_with_hits(self, research_id: int | str) -> dict | None:
        rid = str(research_id)
        doc = self._coll().document(rid).get()
        if not doc.exists:
            return None
        research = self._to_dict(doc)
        hit_docs = list(self._hits_coll(rid).stream())
        # Prefer denormalized signal snapshots on hit docs — never N+1 fetch signals.
        hits = []
        for h in hit_docs:
            hdata = h.to_dict() or {}
            sid = str(hdata.get("signal_id", ""))
            signal = hdata.get("signal")
            if not isinstance(signal, dict):
                signal = {
                    "id": sid,
                    "source": "",
                    "outlet": "",
                    "title": "",
                    "body": "",
                    "url": "",
                    "categories": [],
                    "published_utc": "",
                }
            hits.append({
                "id": h.id,
                "research_id": rid,
                "signal_id": sid,
                "match_reason": hdata.get("match_reason", ""),
                "score": hdata.get("score", 0.0),
                "signal": signal,
                "created_at": hdata.get("created_at"),
            })
        hits.sort(key=lambda h: -(h.get("score") or 0))
        research["hits"] = hits
        research["hit_count"] = len(hits)
        return research

    def replace_hits(self, research_id: int | str, hits: list[dict]) -> None:
        rid = str(research_id)
        hits_ref = self._hits_coll(rid)
        existing = list(hits_ref.stream())
        batch = self._db.batch()
        ops = 0
        for doc in existing:
            batch.delete(doc.reference)
            ops += 1
            if ops >= 400:
                batch.commit()
                batch = self._db.batch()
                ops = 0
        now = _utcnow_iso()
        for h in hits:
            sid = str(h["signal_id"])
            ref = hits_ref.document(sid)
            batch.set(ref, self._hit_payload(h, now=now))
            ops += 1
            if ops >= 400:
                batch.commit()
                batch = self._db.batch()
                ops = 0
        if ops:
            batch.commit()

    def add_hits(self, research_id: int | str, hits: list[dict]) -> int:
        rid = str(research_id)
        hits_ref = self._hits_coll(rid)
        existing_sids = {doc.id for doc in hits_ref.stream()}
        batch = self._db.batch()
        added = 0
        now = _utcnow_iso()
        for h in hits:
            sid = str(h["signal_id"])
            if sid in existing_sids:
                continue
            ref = hits_ref.document(sid)
            batch.set(ref, self._hit_payload(h, now=now))
            added += 1
            if added % 400 == 0:
                batch.commit()
                batch = self._db.batch()
        if added % 400 != 0:
            batch.commit()
        return added

    def update_research(self, research_id: int | str, **fields: Any) -> None:
        fields["updated_at"] = _utcnow_iso()
        self._coll().document(str(research_id)).update(fields)

    def delete_research(self, research_id: int | str) -> bool:
        rid = str(research_id)
        doc = self._coll().document(rid).get()
        if not doc.exists:
            return False
        hits_ref = self._hits_coll(rid)
        existing = list(hits_ref.stream())
        batch = self._db.batch()
        ops = 0
        for h in existing:
            batch.delete(h.reference)
            ops += 1
            if ops >= 400:
                batch.commit()
                batch = self._db.batch()
                ops = 0
        batch.delete(self._coll().document(rid))
        batch.commit()
        return True
