"""Resident reports + community verification votes."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.auth import get_current_user, login_required
from backend.config import DATA_BACKEND
from backend.models import utcnow
from backend.store import get_signal_store, get_vote_store
from backend.db import get_session
from backend.models import IssueVote, Signal, utcnow
from backend.stable_id import compute_stable_id

bp = Blueprint("reports", __name__)


def _vote_payload(vote_store, signal_id, *, user_id):
    summary = vote_store.summarize_votes([signal_id], user_id=user_id).get(
        str(signal_id), {"up": 0, "down": 0, "mine": None}
    )
    return {"signal_id": signal_id, **summary}


@bp.post("/api/reports")
def create_report():
    """Create a resident CivicSignal row."""
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

    store = get_signal_store()
    signal = store.create_signal(
        source="resident",
    db = get_session()
    source = "resident"
    url = (body.get("url") or "").strip()
    body_text = (body.get("body") or "").strip()
    stable_id = compute_stable_id(source, url, title, body_text, metadata=metadata)
    metadata = {**metadata, "stable_id": stable_id}
    signal = Signal(
        stable_id=stable_id,
        source=source,
        outlet=(body.get("outlet") or "Resident report").strip() or "Resident report",
        title=title,
        body=body_text,
        url=url,
        categories=categories,
        published_utc=published,
        metadata=metadata,
    )
    return jsonify({"signal": signal}), 201


@bp.get("/api/reports")
def list_reports():
    """Resident signals only (also included in GET /api/signals)."""
    store = get_signal_store()
    signals = store.list_signals_by_source("resident")
    return jsonify({
        "count": len(signals),
        "signals": signals,
        "storage": DATA_BACKEND,
    })
    db = get_session()
    rows = (
        db.query(Signal)
        .filter(Signal.source == "resident", Signal.archived_at.is_(None))
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
    user = get_current_user()
    store = get_signal_store()
    signals = store.list_signals_by_source("resident")
    signal_ids = [s["id"] for s in signals]
    vote_store = get_vote_store()
    votes = vote_store.summarize_votes(
        signal_ids, user_id=user["id"] if user else None,
    )
    return jsonify({"count": len(votes), "votes": votes})


@bp.post("/api/votes")
@login_required
def cast_vote():
    """Toggle up/down vote for the current user on a resident signal."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    signal_id = body.get("signal_id")
    if signal_id is None:
        return jsonify({"error": "signal_id is required."}), 400
    try:
        signal_id = int(signal_id) if DATA_BACKEND == "sqlite" else signal_id
    except (TypeError, ValueError):
        return jsonify({"error": "signal_id is required."}), 400

    choice = (body.get("choice") or "").strip().lower()
    if choice not in {"up", "down"}:
        return jsonify({"error": "choice must be 'up' or 'down'."}), 400

    user = get_current_user()
    assert user is not None

    sig_store = get_signal_store()
    signal = sig_store.get_signal(signal_id)
    if signal is None or signal.get("source") != "resident":
        return jsonify({"error": "Resident report not found."}), 404

    vote_store = get_vote_store()
    vote_store.cast_vote(signal_id=signal_id, user_id=user["id"], choice=choice)
    return jsonify(_vote_payload(vote_store, signal_id, user_id=user["id"]))
