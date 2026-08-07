"""Research topics — create, list, detail."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.db import get_session
from backend.models import Research

bp = Blueprint("research", __name__)

VALID_STATUSES = {"draft", "active", "archived"}


@bp.post("/api/researches")
def create_research():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required."}), 400

    topic = (body.get("topic") or "").strip()
    keywords = body.get("keywords") or []
    if not isinstance(keywords, list):
        return jsonify({"error": "keywords must be an array."}), 400
    keywords = [str(k).strip() for k in keywords if str(k).strip()]

    categories = body.get("categories") or []
    if not isinstance(categories, list):
        return jsonify({"error": "categories must be an array."}), 400
    categories = [str(c).strip() for c in categories if str(c).strip()]

    notes = (body.get("notes") or "").strip()

    db = get_session()
    research = Research(
        title=title,
        topic=topic,
        keywords=keywords,
        categories=categories,
        notes=notes,
    )
    db.add(research)
    db.commit()
    db.refresh(research)
    return jsonify({"research": research.to_dict()}), 201


@bp.get("/api/researches")
def list_researches():
    db = get_session()
    rows = db.query(Research).order_by(Research.id.desc()).all()
    return jsonify({
        "count": len(rows),
        "researches": [r.to_dict() for r in rows],
    })


@bp.get("/api/researches/<int:research_id>")
def get_research(research_id: int):
    db = get_session()
    research = db.get(Research, research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404
    return jsonify({"research": research.to_dict()})
