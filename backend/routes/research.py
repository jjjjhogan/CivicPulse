"""Research topics — create, list, detail, archive matching."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.research_match import match_signals as _match_signals
from backend.store import get_job_store, get_research_store, get_signal_store

bp = Blueprint("research", __name__)


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


@bp.patch("/api/researches/<research_id>")
def update_research(research_id: str):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    store = get_research_store()
    research = store.get_research(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    allowed = {"title", "topic", "keywords", "categories", "notes", "status"}
    updates = {}
    for key in allowed:
        if key in body:
            val = body[key]
            if key in ("keywords", "categories"):
                if not isinstance(val, list):
                    return jsonify({"error": f"{key} must be an array."}), 400
                val = [str(v).strip() for v in val if str(v).strip()]
            elif key == "status":
                valid_statuses = {"draft", "active", "gathering", "ready", "stale"}
                if val not in valid_statuses:
                    return jsonify({"error": f"Invalid status. Must be one of: {', '.join(sorted(valid_statuses))}"}), 400
            elif key == "title":
                val = (val or "").strip()
                if not val:
                    return jsonify({"error": "title cannot be empty."}), 400
            else:
                val = (val or "").strip()
            updates[key] = val

    if not updates:
        return jsonify({"error": "No valid fields to update."}), 400

    store.update_research(research_id, **updates)
    updated = store.get_research_with_hits(research_id)
    return jsonify({"research": updated})


@bp.delete("/api/researches/<research_id>")
def delete_research(research_id: str):
    store = get_research_store()
    deleted = store.delete_research(research_id)
    if not deleted:
        return jsonify({"error": "Research not found."}), 404
    return jsonify({"deleted": True})


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


@bp.get("/api/researches/<research_id>/jobs")
def list_research_jobs(research_id: str):
    research_store = get_research_store()
    research = research_store.get_research(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404
    job_store = get_job_store()
    jobs = job_store.list_jobs_for_research(research_id)
    return jsonify({"jobs": jobs})
