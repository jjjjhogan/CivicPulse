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

    listen = research.get("listen_sources", [])
    signal_store = get_signal_store()
    all_signals = signal_store.list_signals()
    matched = _match_signals(
        all_signals, research.get("categories", []), research.get("keywords", []),
        listen_sources=listen or None,
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


import re as _re


_NEGATIVE_WORDS = {"not", "no", "never", "don't", "doesn't", "can't", "won't", "stop", "against", "hate", "worst", "terrible", "awful", "angry", "fear", "afraid", "unsafe", "dangerous", "failed", "broken", "ruined"}
_POSITIVE_WORDS = {"love", "great", "good", "best", "happy", "support", "thank", "hope", "better", "improved", "safe", "clean", "beautiful", "wonderful", "excellent", "proud"}
_POLICY_PATTERNS = [
    _re.compile(r"\b(should|must|need to|needs to|ought to|has to|have to)\b", _re.I),
    _re.compile(r"\b(we need|city should|council should|they should|please fix|demand)\b", _re.I),
]
_BOT_INDICATORS = _re.compile(r"(follow me|click link|check bio|dm for|free money|giveaway|subscribe)", _re.I)


def _run_extract_tools(extract: list[str], hits: list[dict]) -> dict:
    sections: dict = {}

    signals = [(h.get("signal") or {}) for h in hits]

    if "sentiment" in extract:
        positive = negative = neutral = 0
        for sig in signals:
            text = ((sig.get("title") or "") + " " + (sig.get("body") or "")).lower()
            words = set(text.split())
            pos = len(words & _POSITIVE_WORDS)
            neg = len(words & _NEGATIVE_WORDS)
            if pos > neg:
                positive += 1
            elif neg > pos:
                negative += 1
            else:
                neutral += 1
        sections["sentiment"] = {
            "label": "Sentiment & emotion",
            "total_signals": len(hits),
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
        }

    if "clustering" in extract:
        cat_groups: dict[str, int] = {}
        for sig in signals:
            for cat in sig.get("categories", []):
                cat_groups[cat] = cat_groups.get(cat, 0) + 1
        sections["clustering"] = {
            "label": "Narrative clustering",
            "clusters": cat_groups,
            "cluster_count": len(cat_groups),
        }

    if "demographics" in extract:
        source_counts: dict[str, int] = {}
        for sig in signals:
            src = sig.get("source", "unknown")
            source_counts[src] = source_counts.get(src, 0) + 1
        sections["demographics"] = {
            "label": "Voice demographics",
            "by_source": source_counts,
            "note": "Broken down by source platform. Renter/owner inference not yet available.",
        }

    if "policy" in extract:
        asks: list[str] = []
        for sig in signals:
            text = (sig.get("title") or "") + " " + (sig.get("body") or "")
            for pat in _POLICY_PATTERNS:
                if pat.search(text):
                    snippet = (sig.get("title") or text[:80]).strip()
                    if snippet and snippet not in asks:
                        asks.append(snippet)
                    break
        sections["policy"] = {
            "label": "Policy asks extraction",
            "asks": asks[:20],
            "total_detected": len(asks),
        }

    if "misinfo" in extract:
        flagged = 0
        for sig in signals:
            text = ((sig.get("title") or "") + " " + (sig.get("body") or "")).lower()
            if "hoax" in text or "fake news" in text or "conspiracy" in text or "debunked" in text:
                flagged += 1
        sections["misinfo"] = {
            "label": "Misinformation flags",
            "flagged_count": flagged,
            "total_signals": len(hits),
            "note": "Conservative keyword-based scan. Full fact-check pipeline not yet available.",
        }

    if "bots" in extract:
        suspected = 0
        for sig in signals:
            text = ((sig.get("title") or "") + " " + (sig.get("body") or ""))
            if _BOT_INDICATORS.search(text):
                suspected += 1
        sections["bots"] = {
            "label": "Bot & brigading detection",
            "suspected_count": suspected,
            "total_signals": len(hits),
            "note": "Heuristic keyword scan. ML-based detection not yet available.",
        }

    return sections


@bp.get("/api/researches/<research_id>/summary")
def research_summary(research_id: str):
    store = get_research_store()
    research = store.get_research_with_hits(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    extract = research.get("extract", [])
    hits = research.get("hits", [])
    sections = _run_extract_tools(extract, hits)

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

    from backend.research_match import SOURCE_MAP

    signal_store = get_signal_store()
    all_signals = signal_store.list_signals()

    if listen_sources:
        allowed = {SOURCE_MAP.get(s, s) for s in listen_sources}
        filtered = [s for s in all_signals if s.get("source", "") in allowed]
    else:
        filtered = all_signals

    archive_count = len(filtered)
    source_count = len(listen_sources) if listen_sources else 1
    window_mul = {"7d": 0.35, "30d": 1.0, "90d": 2.4, "ytd": 3.1}.get(time_window, 1.0)

    estimated_voices = int(archive_count * window_mul)
    coverage = min(97, 48 + source_count * 8)

    return jsonify({
        "archive_count": archive_count,
        "estimated_voices": estimated_voices,
        "coverage_pct": coverage,
        "time_window": time_window,
        "sources_on": source_count,
        "label": "estimate",
    })


@bp.post("/api/researches/<research_id>/launch")
def launch_research(research_id: str):
    store = get_research_store()
    research = store.get_research(research_id)
    if research is None:
        return jsonify({"error": "Research not found."}), 404

    store.update_research(research_id, status="active")

    listen = research.get("listen_sources", [])
    extract = research.get("extract", [])

    matched: list[dict] = []
    if research.get("categories") or research.get("keywords"):
        signal_store = get_signal_store()
        all_signals = signal_store.list_signals()
        matched = _match_signals(
            all_signals,
            research.get("categories", []),
            research.get("keywords", []),
            listen_sources=listen or None,
        )
        store.replace_hits(research_id, matched)

    sections = _run_extract_tools(extract, matched)

    updated = store.get_research_with_hits(research_id)
    return jsonify({
        "research": updated,
        "hit_count": len(matched),
        "extract_sections": list(sections.keys()),
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
