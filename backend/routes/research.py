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

    extract = body.get("extract") or []
    if not isinstance(extract, list):
        return jsonify({"error": "extract must be an array."}), 400
    extract = [str(e).strip() for e in extract if str(e).strip()]

    listen_sources = body.get("listen_sources") or []
    if not isinstance(listen_sources, list):
        return jsonify({"error": "listen_sources must be an array."}), 400
    listen_sources = [str(s).strip() for s in listen_sources if str(s).strip()]

    languages = body.get("languages") or []
    if not isinstance(languages, list):
        return jsonify({"error": "languages must be an array."}), 400
    languages = [str(l).strip() for l in languages if str(l).strip()]

    time_window = (body.get("time_window") or "30d").strip()
    geo_radius = (body.get("geo_radius") or "irvine").strip()
    notes = (body.get("notes") or "").strip()

    store = get_research_store()
    research = store.create_research(
        title=title, topic=topic, keywords=keywords,
        categories=categories, extract=extract,
        listen_sources=listen_sources, languages=languages,
        time_window=time_window, geo_radius=geo_radius,
        notes=notes,
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

    allowed = {
        "title", "topic", "keywords", "categories", "notes", "status",
        "extract", "listen_sources", "languages", "time_window", "geo_radius",
    }
    list_fields = {"keywords", "categories", "extract", "listen_sources", "languages"}
    updates = {}
    for key in allowed:
        if key in body:
            val = body[key]
            if key in list_fields:
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


@bp.get("/api/researches/<research_id>/summary")
def research_summary(research_id: str):
    store = get_research_store()
    research = store.get_research_with_hits(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    extract = research.get("extract", [])
    hits = research.get("hits", [])

    sections: dict = {}

    if "sentiment" in extract:
        positive = sum(1 for h in hits if (h.get("signal") or {}).get("categories") and True)
        sections["sentiment"] = {
            "label": "Sentiment & emotion",
            "total_signals": len(hits),
            "note": "Sentiment analysis across matched signals.",
        }

    if "clustering" in extract:
        cat_groups: dict[str, int] = {}
        for h in hits:
            sig = h.get("signal") or {}
            for cat in sig.get("categories", []):
                cat_groups[cat] = cat_groups.get(cat, 0) + 1
        sections["clustering"] = {
            "label": "Narrative clustering",
            "clusters": cat_groups,
            "note": "Signals grouped by category/topic.",
        }

    if "demographics" in extract:
        sections["demographics"] = {
            "label": "Voice demographics",
            "note": "Demographic inference not yet implemented — placeholder.",
        }

    if "policy" in extract:
        sections["policy"] = {
            "label": "Policy asks extraction",
            "note": "Policy extraction not yet implemented — placeholder.",
        }

    if "misinfo" in extract:
        sections["misinfo"] = {
            "label": "Misinformation flags",
            "note": "Misinformation detection not yet implemented — placeholder.",
        }

    if "bots" in extract:
        sections["bots"] = {
            "label": "Bot & brigading detection",
            "note": "Bot detection not yet implemented — placeholder.",
        }

    sources_used: list[str] = []
    for h in hits:
        sig = h.get("signal") or {}
        src = sig.get("source", "")
        if src and src not in sources_used:
            sources_used.append(src)

    return jsonify({
        "research_id": research.get("id"),
        "title": research.get("title", ""),
        "status": research.get("status", ""),
        "hit_count": len(hits),
        "extract": extract,
        "sections": sections,
        "sources_used": sources_used,
        "time_window": research.get("time_window", "30d"),
        "geo_radius": research.get("geo_radius", "irvine"),
    })


@bp.post("/api/researches/preview")
def preview_metrics():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    listen_sources = body.get("listen_sources") or []
    time_window = body.get("time_window") or "30d"

    signal_store = get_signal_store()
    all_signals = signal_store.list_signals()
    archive_count = len(all_signals)

    source_count = len(listen_sources) if listen_sources else 1
    window_mul = {"7d": 0.35, "30d": 1.0, "90d": 2.4, "ytd": 3.1}.get(time_window, 1.0)

    estimated_voices = int(archive_count * source_count * window_mul)
    coverage = min(97, 48 + source_count * 8)

    return jsonify({
        "archive_count": archive_count,
        "estimated_voices": estimated_voices,
        "coverage_pct": coverage,
        "time_window": time_window,
        "sources_on": source_count,
        "label": "estimate",
    })


IMPLEMENTED_SOURCES: dict[str, str] = {
    "news311": "irvine-news",
    "tiktok": "tiktok",
}


@bp.post("/api/researches/<research_id>/launch")
def launch_research(research_id: str):
    store = get_research_store()
    research = store.get_research(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    store.update_research(research_id, status="gathering")

    if research.get("categories") or research.get("keywords"):
        signal_store = get_signal_store()
        all_signals = signal_store.list_signals()
        matched = _match_signals(
            all_signals, research.get("categories", []), research.get("keywords", []),
        )
        store.replace_hits(research_id, matched)

    listen = research.get("listen_sources", [])
    queued: list[str] = []
    skipped: list[str] = []
    for src in listen:
        scraper_source = IMPLEMENTED_SOURCES.get(src)
        if scraper_source:
            queued.append(src)
        else:
            skipped.append(src)

    updated = store.get_research_with_hits(research_id)
    return jsonify({
        "research": updated,
        "queued_sources": queued,
        "skipped_sources": skipped,
    })


VOICE_EXTRAS: dict[str, list[str]] = {
    "housing": ["can't afford rent", "priced out", "airbnb listings", "landlord issues"],
    "potholes": ["car bottomed out", "street never fixed", "detour forever"],
    "noise": ["can't sleep", "leaf blowers at 7am", "party next door"],
    "sanitation": ["missed pickup", "rats in the alley", "overflowing bins"],
    "public_safety": ["streetlight out", "don't walk at night", "more patrols"],
    "violent_crime": ["shots fired", "unsafe after dark"],
    "property_crime": ["package theft", "catalytic converter"],
    "traffic_safety": ["speeding on my street", "need a crosswalk"],
    "emergencies": ["flooded garage", "evacuation route"],
    "immigration": ["ice rumor", "know your rights"],
}


@bp.post("/api/suggest/expansions")
def suggest_expansions():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    title = (body.get("title") or "").strip()
    if len(title) < 12:
        return jsonify({"voice_chips": [], "civic_chips": [], "categories": []})

    from scrapers.categories import DEFAULT_SEARCH_TERMS

    category_keywords: dict[str, list[str]] = {
        cat.value: terms for cat, terms in DEFAULT_SEARCH_TERMS.items()
    }

    lower = title.lower()
    matched_cats: list[str] = []
    for cat, terms in category_keywords.items():
        if any(t.lower() in lower for t in terms):
            matched_cats.append(cat)
            continue
        if cat.replace("_", " ") in lower:
            matched_cats.append(cat)

    if not matched_cats:
        for cat in VOICE_EXTRAS:
            if cat.replace("_", " ") in lower:
                matched_cats.append(cat)

    seen: set[str] = set()
    voice_chips: list[str] = []
    civic_chips: list[str] = []

    for cat in matched_cats:
        for phrase in VOICE_EXTRAS.get(cat, []):
            key = phrase.lower()
            if key not in seen:
                seen.add(key)
                voice_chips.append(phrase)
        for term in category_keywords.get(cat, [])[:4]:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                civic_chips.append(term)

    for word in lower.split():
        if len(word) >= 5 and word not in seen and len(voice_chips) + len(civic_chips) < 12:
            seen.add(word)
            civic_chips.append(word)

    voice_chips = voice_chips[:12]
    civic_chips = civic_chips[:12]

    return jsonify({
        "voice_chips": voice_chips,
        "civic_chips": civic_chips,
        "categories": matched_cats,
    })
