"""Research topics — create, list, detail, archive matching."""

from __future__ import annotations

import re

from flask import Blueprint, jsonify, request

from backend.store import get_research_store, get_signal_store

bp = Blueprint("research", __name__)


def _match_signals(
    signals: list[dict],
    categories: list[str],
    keywords: list[str],
) -> list[dict]:
    """Find signals matching given categories and/or keywords.

    Returns a list of dicts with signal_id, match_reason, and score.
    """
    research_cats = set(categories or [])
    research_kws = [kw.lower() for kw in (keywords or []) if kw.strip()]

    hits = []
    for signal in signals:
        reasons = []
        score = 0.0

        signal_cats = set(signal.get("categories") or [])
        overlap = research_cats & signal_cats
        if overlap:
            reasons.append("category:" + ",".join(sorted(overlap)))
            score += 0.5 * len(overlap)

        text = ((signal.get("title") or "") + " " + (signal.get("body") or "")).lower()
        matched_kws = []
        for kw in research_kws:
            if re.search(r"\b" + re.escape(kw), text):
                matched_kws.append(kw)
                score += 0.3

        if matched_kws:
            reasons.append("keyword:" + ",".join(matched_kws))

        if reasons:
            hits.append({
                "signal_id": signal["id"],
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

    store = get_research_store()
    research = store.create_research(
        title=title, topic=topic, keywords=keywords,
        categories=categories, notes=notes,
    )
    return jsonify({"research": research}), 201


@bp.get("/api/researches")
def list_researches():
    store = get_research_store()
    rows = store.list_researches()
    return jsonify({"count": len(rows), "researches": rows})


@bp.get("/api/researches/<research_id>")
def get_research(research_id: str):
    store = get_research_store()
    research = store.get_research_with_hits(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404
    return jsonify({"research": research})


@bp.post("/api/researches/<research_id>/archive")
def run_archive(research_id: str):
    research_store = get_research_store()
    research = research_store.get_research(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    if not (research.get("categories") or research.get("keywords")):
        return jsonify({"error": "Research needs at least one category or keyword."}), 400

    signal_store = get_signal_store()
    all_signals = signal_store.list_signals()
    matched = _match_signals(
        all_signals, research.get("categories", []), research.get("keywords", []),
    )

    research_store.replace_hits(research_id, matched)
    if research.get("status") == "draft":
        research_store.update_research(research_id, status="active")

    updated = research_store.get_research_with_hits(research_id)
    return jsonify({"research": updated, "matched": len(matched)})
