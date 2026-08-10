"""Research topics — create, list, detail, archive matching."""

from __future__ import annotations

import re

from flask import Blueprint, jsonify, request

from backend.db import get_session
from backend.models import Research, ResearchHit, Signal

bp = Blueprint("research", __name__)


def _match_signals(db, research: Research) -> list[dict]:
    """Find signals matching a research's categories and/or keywords.

    Returns a list of dicts with signal_id, match_reason, and score.
    Score is the sum of category matches (0.5 each) + keyword matches (0.3 each).
    """
    signals = db.query(Signal).all()
    research_cats = set(research.categories or [])
    research_kws = [kw.lower() for kw in (research.keywords or []) if kw.strip()]

    hits = []
    for signal in signals:
        reasons = []
        score = 0.0

        signal_cats = set(signal.categories or [])
        overlap = research_cats & signal_cats
        if overlap:
            reasons.append("category:" + ",".join(sorted(overlap)))
            score += 0.5 * len(overlap)

        text = ((signal.title or "") + " " + (signal.body or "")).lower()
        matched_kws = []
        for kw in research_kws:
            if re.search(r"\b" + re.escape(kw), text):
                matched_kws.append(kw)
                score += 0.3

        if matched_kws:
            reasons.append("keyword:" + ",".join(matched_kws))

        if reasons:
            hits.append({
                "signal_id": signal.id,
                "match_reason": "; ".join(reasons),
                "score": round(score, 2),
            })

    hits.sort(key=lambda h: -h["score"])
    return hits


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
    return jsonify({"research": research.to_dict(include_hits=True)})


@bp.post("/api/researches/<int:research_id>/archive")
def run_archive(research_id: int):
    db = get_session()
    research = db.get(Research, research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    if not (research.categories or research.keywords):
        return jsonify({"error": "Research needs at least one category or keyword."}), 400

    db.query(ResearchHit).filter(ResearchHit.research_id == research_id).delete()

    matched = _match_signals(db, research)
    for m in matched:
        db.add(ResearchHit(
            research_id=research_id,
            signal_id=m["signal_id"],
            match_reason=m["match_reason"],
            score=m["score"],
        ))

    if research.status == "draft":
        research.status = "active"

    db.commit()
    db.refresh(research)

    return jsonify({
        "research": research.to_dict(include_hits=True),
        "matched": len(matched),
    })
