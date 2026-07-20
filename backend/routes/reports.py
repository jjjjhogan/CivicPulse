"""Resident reports + community verification votes (SQLite)."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from backend.auth import get_current_user, login_required
from backend.db import get_session
from backend.models import IssueVote, Signal, utcnow

bp = Blueprint("reports", __name__)


def _summarize_votes(db, signal_ids: list[int], *, user_id: int | None) -> dict[str, dict]:
    """Return {signal_id_str: {up, down, mine}} for the given signals."""
    result = {str(sid): {"up": 0, "down": 0, "mine": None} for sid in signal_ids}
    if not signal_ids:
        return result

    rows = db.scalars(
        select(IssueVote).where(IssueVote.signal_id.in_(signal_ids))
    ).all()

    for row in rows:
        bucket = result[str(row.signal_id)]
        if row.choice in {"up", "down"}:
            bucket[row.choice] += 1
        if user_id is not None and row.user_id == user_id:
            bucket["mine"] = row.choice

    return result


def _vote_payload(db, signal_id: int, *, user_id: int | None) -> dict:
    summary = _summarize_votes(db, [signal_id], user_id=user_id).get(
        str(signal_id), {"up": 0, "down": 0, "mine": None}
    )
    return {"signal_id": signal_id, **summary}


@bp.post("/api/reports")
def create_report():
    """Create a resident CivicSignal row in SQLite."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required."}), 400

    categories = body.get("categories") or []
    if not isinstance(categories, list) or not categories:
        return jsonify({"error": "Select at least one category."}), 400
    categories = [str(c).strip() for c in categories if str(c).strip()]
    if not categories:
        return jsonify({"error": "Select at least one category."}), 400

    metadata = body.get("metadata") or body.get("extra") or {}
    if not isinstance(metadata, dict):
        return jsonify({"error": "metadata must be a JSON object."}), 400

    lat = metadata.get("lat")
    lng = metadata.get("lng")
    if lat is None or lng is None:
        return jsonify({"error": "metadata.lat and metadata.lng are required."}), 400
    try:
        metadata = {
            **metadata,
            "lat": float(lat),
            "lng": float(lng),
            "address": str(metadata.get("address") or "").strip(),
            "reporter_name": str(metadata.get("reporter_name") or "").strip(),
            "reporter_email": str(metadata.get("reporter_email") or "").strip(),
            "reporter_phone": str(metadata.get("reporter_phone") or "").strip(),
        }
    except (TypeError, ValueError):
        return jsonify({"error": "metadata.lat and metadata.lng must be numbers."}), 400

    if not metadata["address"]:
        return jsonify({"error": "metadata.address is required."}), 400

    published = (body.get("published_utc") or "").strip()
    if not published:
        published = utcnow().date().isoformat()

    db = get_session()
    signal = Signal(
        source="resident",
        outlet=(body.get("outlet") or "Resident report").strip() or "Resident report",
        title=title,
        body=(body.get("body") or "").strip(),
        url=(body.get("url") or "").strip(),
        categories=categories,
        published_utc=published,
        extra=metadata,
    )
    db.add(signal)
    db.commit()
    db.refresh(signal)
    return jsonify({"signal": signal.to_dict()}), 201


@bp.get("/api/reports")
def list_reports():
    """Resident signals only (also included in GET /api/signals)."""
    db = get_session()
    rows = (
        db.query(Signal)
        .filter(Signal.source == "resident")
        .order_by(Signal.id.desc())
        .all()
    )
    return jsonify(
        {
            "count": len(rows),
            "signals": [row.to_dict() for row in rows],
            "storage": "db",
        }
    )


@bp.get("/api/votes")
def list_votes():
    """Vote tallies for resident reports. Includes mine when logged in."""
    db = get_session()
    user = get_current_user()
    rows = (
        db.query(Signal)
        .filter(Signal.source == "resident")
        .order_by(Signal.id.asc())
        .all()
    )
    signal_ids = [row.id for row in rows]
    votes = _summarize_votes(
        db, signal_ids, user_id=user.id if user else None
    )
    return jsonify({"count": len(votes), "votes": votes})


@bp.post("/api/votes")
@login_required
def cast_vote():
    """Toggle up/down vote for the current user on a resident signal."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    try:
        signal_id = int(body.get("signal_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "signal_id is required."}), 400

    choice = (body.get("choice") or "").strip().lower()
    if choice not in {"up", "down"}:
        return jsonify({"error": "choice must be 'up' or 'down'."}), 400

    user = get_current_user()
    assert user is not None

    db = get_session()
    signal = db.get(Signal, signal_id)
    if signal is None or signal.source != "resident":
        return jsonify({"error": "Resident report not found."}), 404

    existing = db.scalar(
        select(IssueVote).where(
            IssueVote.signal_id == signal_id,
            IssueVote.user_id == user.id,
        )
    )

    if existing is not None and existing.choice == choice:
        db.delete(existing)
        db.commit()
    elif existing is not None:
        existing.choice = choice
        existing.updated_at = utcnow()
        db.commit()
    else:
        db.add(
            IssueVote(
                signal_id=signal_id,
                user_id=user.id,
                choice=choice,
            )
        )
        db.commit()

    return jsonify(_vote_payload(db, signal_id, user_id=user.id))
