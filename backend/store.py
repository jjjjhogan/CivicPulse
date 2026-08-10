"""Store protocols — abstracts data access across SQLite and Firestore."""

from __future__ import annotations

from typing import Any, Protocol


# ---------------------------------------------------------------------------
# Protocols
# ---------------------------------------------------------------------------

class SignalStore(Protocol):
    def list_signals(self) -> list[dict]: ...
    def list_feed_signals(self) -> list[dict]: ...
    def get_signal(self, signal_id: int | str) -> dict | None: ...
    def create_signal(self, **fields: Any) -> dict: ...
    def list_signals_by_source(self, source: str) -> list[dict]: ...


class UserStore(Protocol):
    def get_user(self, user_id: int | str) -> dict | None: ...
    def get_user_by_email(self, email: str) -> dict | None: ...
    def create_user(self, *, name: str, email: str, password_hash: str) -> dict: ...


class JobStore(Protocol):
    def create_job(self, *, source: str, settings: dict, user_id: Any = None) -> dict: ...
    def get_job(self, job_id: int | str) -> dict | None: ...
    def list_jobs(self, *, limit: int = 20) -> list[dict]: ...
    def update_job(self, job_id: int | str, **fields: Any) -> None: ...
    def get_running_job(self) -> dict | None: ...
    def get_latest_job(self) -> dict | None: ...


class VoteStore(Protocol):
    def summarize_votes(
        self, signal_ids: list, *, user_id: Any = None,
    ) -> dict[str, dict]: ...
    def cast_vote(
        self, *, signal_id: Any, user_id: Any, choice: str,
    ) -> None: ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def public_user(user: dict) -> dict:
    """Strip password_hash from a user dict for API responses."""
    return {"id": user["id"], "email": user["email"], "name": user["name"]}


# ---------------------------------------------------------------------------
# Flask-context factories (use inside request handlers)
# ---------------------------------------------------------------------------

def get_signal_store() -> SignalStore:
    from backend.config import DATA_BACKEND
    if DATA_BACKEND == "firestore":
        from backend.firestore import get_firestore_client
        from backend.store_firestore import FirestoreSignalStore
        return FirestoreSignalStore(get_firestore_client())
    from backend.db import get_session
    from backend.store_sqlite import SQLiteSignalStore
    return SQLiteSignalStore(get_session())


def get_user_store() -> UserStore:
    from backend.config import DATA_BACKEND
    if DATA_BACKEND == "firestore":
        from backend.firestore import get_firestore_client
        from backend.store_firestore import FirestoreUserStore
        return FirestoreUserStore(get_firestore_client())
    from backend.db import get_session
    from backend.store_sqlite import SQLiteUserStore
    return SQLiteUserStore(get_session())


def get_job_store() -> JobStore:
    from backend.config import DATA_BACKEND
    if DATA_BACKEND == "firestore":
        from backend.firestore import get_firestore_client
        from backend.store_firestore import FirestoreJobStore
        return FirestoreJobStore(get_firestore_client())
    from backend.db import get_session
    from backend.store_sqlite import SQLiteJobStore
    return SQLiteJobStore(get_session())


def get_vote_store() -> VoteStore:
    from backend.config import DATA_BACKEND
    if DATA_BACKEND == "firestore":
        from backend.firestore import get_firestore_client
        from backend.store_firestore import FirestoreVoteStore
        return FirestoreVoteStore(get_firestore_client())
    from backend.db import get_session
    from backend.store_sqlite import SQLiteVoteStore
    return SQLiteVoteStore(get_session())


# ---------------------------------------------------------------------------
# Standalone factories (outside Flask request — e.g. job runner threads)
# ---------------------------------------------------------------------------

def get_job_store_standalone() -> JobStore:
    from backend.config import DATA_BACKEND
    if DATA_BACKEND == "firestore":
        from backend.firestore import get_firestore_client
        from backend.store_firestore import FirestoreJobStore
        return FirestoreJobStore(get_firestore_client())
    from backend.db import SessionLocal, get_engine
    get_engine()
    return _SQLiteJobStoreStandalone(SessionLocal)


class _SQLiteJobStoreStandalone:
    """Job store for background threads — creates/closes sessions per call."""

    def __init__(self, session_factory) -> None:
        self._factory = session_factory

    def get_job(self, job_id: int | str) -> dict | None:
        from backend.models import ScrapeJob
        db = self._factory()
        try:
            job = db.get(ScrapeJob, int(job_id))
            return job.to_dict() if job else None
        finally:
            db.close()

    def update_job(self, job_id: int | str, **fields) -> None:
        from backend.models import ScrapeJob
        db = self._factory()
        try:
            job = db.get(ScrapeJob, int(job_id))
            if job is None:
                return
            for k, v in fields.items():
                setattr(job, k, v)
            db.commit()
        finally:
            db.close()

    def create_job(self, **kw):
        raise NotImplementedError

    def list_jobs(self, **kw):
        raise NotImplementedError

    def get_running_job(self):
        raise NotImplementedError

    def get_latest_job(self):
        raise NotImplementedError
