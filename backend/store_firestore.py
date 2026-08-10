"""Firestore stores."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

def _doc_to_signal_dict(doc) -> dict:
    data = doc.to_dict()
    return {
        "id": doc.id,
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
    data = doc.to_dict()
    return {
        "outlet": data.get("outlet", ""),
        "title": data.get("title", ""),
        "categories": data.get("categories", []),
        "published_utc": data.get("published_utc", ""),
    }


class FirestoreSignalStore:
    COLLECTION = "signals"

    def __init__(self, db) -> None:
        self._db = db

    def _coll(self):
        return self._db.collection(self.COLLECTION)

    def list_signals(self) -> list[dict]:
        docs = self._coll().order_by("created_at").stream()
        return [_doc_to_signal_dict(doc) for doc in docs]

    def list_feed_signals(self) -> list[dict]:
        docs = self._coll().order_by("created_at").stream()
        return [_doc_to_feed_dict(doc) for doc in docs]

    def get_signal(self, signal_id: int | str) -> dict | None:
        doc = self._coll().document(str(signal_id)).get()
        if not doc.exists:
            return None
        return _doc_to_signal_dict(doc)

    def create_signal(self, **fields: Any) -> dict:
        data = {
            "source": fields.get("source", ""),
            "outlet": fields.get("outlet", ""),
            "title": fields.get("title", ""),
            "body": fields.get("body", ""),
            "url": fields.get("url", ""),
            "categories": fields.get("categories", []),
            "published_utc": fields.get("published_utc", ""),
            "metadata": fields.get("metadata", {}),
            "created_at": _utcnow_iso(),
        }
        _, doc_ref = self._coll().add(data)
        return {**data, "id": doc_ref.id}

    def list_signals_by_source(self, source: str) -> list[dict]:
        docs = (
            self._coll()
            .where("source", "==", source)
            .order_by("created_at", direction="DESCENDING")
            .stream()
        )
        return [_doc_to_signal_dict(doc) for doc in docs]


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
            "created_at": data.get("created_at"),
            "started_at": data.get("started_at"),
            "finished_at": data.get("finished_at"),
        }

    def create_job(self, *, source: str, settings: dict, user_id: Any = None) -> dict:
        data = {
            "source": source,
            "status": "pending",
            "settings": settings or {},
            "command": None,
            "log": "",
            "error": None,
            "exit_code": None,
            "user_id": str(user_id) if user_id else None,
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
            .order_by("created_at", direction="DESCENDING")
            .limit(1)
            .stream()
        )
        return self._to_dict(docs[0]) if docs else None

    def get_latest_job(self) -> dict | None:
        docs = list(
            self._coll()
            .order_by("created_at", direction="DESCENDING")
            .limit(1)
            .stream()
        )
        return self._to_dict(docs[0]) if docs else None


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
        batch_size = 30
        for i in range(0, len(str_ids), batch_size):
            chunk = str_ids[i : i + batch_size]
            docs = self._coll().where("signal_id", "in", chunk).stream()
            for doc in docs:
                data = doc.to_dict()
                sid = str(data.get("signal_id", ""))
                if sid not in result:
                    continue
                choice = data.get("choice", "")
                if choice in {"up", "down"}:
                    result[sid][choice] += 1
                if user_id is not None and str(data.get("user_id", "")) == str(user_id):
                    result[sid]["mine"] = choice
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
