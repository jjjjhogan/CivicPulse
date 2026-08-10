"""SQLite stores — wraps existing SQLAlchemy queries."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import IssueVote, ScrapeJob, Signal, User, utcnow


# ---------------------------------------------------------------------------
# Signals
# ---------------------------------------------------------------------------

class SQLiteSignalStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_signals(self) -> list[dict]:
        rows = self._db.query(Signal).order_by(Signal.id.asc()).all()
        return [row.to_dict() for row in rows]

    def list_feed_signals(self) -> list[dict]:
        rows = self._db.query(Signal).order_by(Signal.id.asc()).all()
        return [row.to_feed_dict() for row in rows]

    def get_signal(self, signal_id: int | str) -> dict | None:
        row = self._db.get(Signal, int(signal_id))
        return row.to_dict() if row else None

    def create_signal(self, **fields: Any) -> dict:
        metadata = fields.pop("metadata", {})
        sig = Signal(**fields, extra=metadata)
        self._db.add(sig)
        self._db.commit()
        self._db.refresh(sig)
        return sig.to_dict()

    def list_signals_by_source(self, source: str) -> list[dict]:
        rows = (
            self._db.query(Signal)
            .filter(Signal.source == source)
            .order_by(Signal.id.desc())
            .all()
        )
        return [row.to_dict() for row in rows]


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

class SQLiteUserStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "password_hash": user.password_hash,
        }

    def get_user(self, user_id: int | str) -> dict | None:
        row = self._db.get(User, int(user_id))
        return self._to_dict(row) if row else None

    def get_user_by_email(self, email: str) -> dict | None:
        row = self._db.query(User).filter_by(email=email).first()
        return self._to_dict(row) if row else None

    def create_user(self, *, name: str, email: str, password_hash: str) -> dict:
        user = User(name=name, email=email, password_hash=password_hash)
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return self._to_dict(user)


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

class SQLiteJobStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def create_job(self, *, source: str, settings: dict, user_id: Any = None) -> dict:
        job = ScrapeJob(source=source, status="pending", settings=settings or {}, user_id=user_id)
        self._db.add(job)
        self._db.commit()
        self._db.refresh(job)
        return job.to_dict()

    def get_job(self, job_id: int | str) -> dict | None:
        row = self._db.get(ScrapeJob, int(job_id))
        return row.to_dict() if row else None

    def list_jobs(self, *, limit: int = 20) -> list[dict]:
        rows = (
            self._db.query(ScrapeJob)
            .order_by(ScrapeJob.id.desc())
            .limit(limit)
            .all()
        )
        return [row.to_dict() for row in rows]

    def update_job(self, job_id: int | str, **fields: Any) -> None:
        job = self._db.get(ScrapeJob, int(job_id))
        if job is None:
            return
        for k, v in fields.items():
            setattr(job, k, v)
        self._db.commit()

    def get_running_job(self) -> dict | None:
        row = (
            self._db.query(ScrapeJob)
            .filter(ScrapeJob.status == "running")
            .order_by(ScrapeJob.id.desc())
            .first()
        )
        return row.to_dict() if row else None

    def get_latest_job(self) -> dict | None:
        row = self._db.query(ScrapeJob).order_by(ScrapeJob.id.desc()).first()
        return row.to_dict() if row else None


# ---------------------------------------------------------------------------
# Votes
# ---------------------------------------------------------------------------

class SQLiteVoteStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def summarize_votes(
        self, signal_ids: list, *, user_id: Any = None,
    ) -> dict[str, dict]:
        result: dict[str, dict] = {
            str(sid): {"up": 0, "down": 0, "mine": None} for sid in signal_ids
        }
        if not signal_ids:
            return result
        rows = self._db.scalars(
            select(IssueVote).where(IssueVote.signal_id.in_(signal_ids))
        ).all()
        for row in rows:
            bucket = result[str(row.signal_id)]
            if row.choice in {"up", "down"}:
                bucket[row.choice] += 1
            if user_id is not None and row.user_id == user_id:
                bucket["mine"] = row.choice
        return result

    def cast_vote(self, *, signal_id: Any, user_id: Any, choice: str) -> None:
        existing = self._db.scalar(
            select(IssueVote).where(
                IssueVote.signal_id == signal_id,
                IssueVote.user_id == user_id,
            )
        )
        if existing is not None and existing.choice == choice:
            self._db.delete(existing)
        elif existing is not None:
            existing.choice = choice
            existing.updated_at = utcnow()
        else:
            self._db.add(IssueVote(signal_id=signal_id, user_id=user_id, choice=choice))
        self._db.commit()
