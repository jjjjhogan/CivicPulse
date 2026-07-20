"""ORM models: User, Signal, ScrapeJob, IssueVote."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from backend.db import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    jobs: Mapped[list[ScrapeJob]] = relationship(back_populates="user")
    votes: Mapped[list[IssueVote]] = relationship(back_populates="user")

    def to_public_dict(self) -> dict:
        return {"id": self.id, "email": self.email, "name": self.name}


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    outlet: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    categories: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    published_utc: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    extra: Mapped[dict] = mapped_column("metadata", JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    votes: Mapped[list[IssueVote]] = relationship(back_populates="signal")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "outlet": self.outlet,
            "title": self.title,
            "body": self.body,
            "url": self.url,
            "categories": self.categories or [],
            "published_utc": self.published_utc,
            "metadata": self.extra or {},
        }

    def to_feed_dict(self) -> dict:
        return {
            "outlet": self.outlet,
            "title": self.title,
            "categories": self.categories or [],
            "published_utc": self.published_utc,
        }


class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    settings: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    command: Mapped[str | None] = mapped_column(Text, nullable=True)
    log: Mapped[str] = mapped_column(Text, nullable=False, default="")
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User | None] = relationship(back_populates="jobs")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "status": self.status,
            "settings": self.settings or {},
            "command": self.command,
            "log": self.log or "",
            "error": self.error,
            "exit_code": self.exit_code,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }


class IssueVote(Base):
    """Community verification vote on a resident-reported Signal."""

    __tablename__ = "issue_votes"
    __table_args__ = (
        UniqueConstraint("signal_id", "user_id", name="uq_issue_vote_signal_user"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    signal_id: Mapped[int] = mapped_column(
        ForeignKey("signals.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    choice: Mapped[str] = mapped_column(String(8), nullable=False)  # up | down
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    signal: Mapped[Signal] = relationship(back_populates="votes")
    user: Mapped[User] = relationship(back_populates="votes")
