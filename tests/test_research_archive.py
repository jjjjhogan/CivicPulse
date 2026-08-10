"""Archive matcher — category + keyword matching against signals."""

from __future__ import annotations


def _create_research(client, **overrides):
    payload = {
        "title": "Housing prices in Irvine",
        "keywords": ["rent", "housing prices", "lease"],
        "categories": ["housing"],
    }
    payload.update(overrides)
    res = client.post("/api/researches", json=payload)
    assert res.status_code == 201
    return res.get_json()["research"]


def _create_signal(client, title, categories, body="", source="news"):
    """Insert a signal via the reports endpoint (source=resident) or directly."""
    from backend.db import get_session
    from backend.models import Signal

    with client.application.app_context():
        db = get_session()
        signal = Signal(
            source=source,
            title=title,
            body=body,
            categories=categories,
        )
        db.add(signal)
        db.commit()
        db.refresh(signal)
        return signal.id


def test_archive_category_match(client):
    _create_signal(client, "Rent hikes across Irvine", ["housing"])
    _create_signal(client, "New park opening", ["sanitation"])
    r = _create_research(client)

    res = client.post(f"/api/researches/{r['id']}/archive")
    assert res.status_code == 200
    data = res.get_json()
    assert data["matched"] >= 1
    hits = data["research"]["hits"]
    titles = [h["signal"]["title"] for h in hits]
    assert "Rent hikes across Irvine" in titles
    assert "New park opening" not in titles


def test_archive_keyword_match(client):
    _create_signal(client, "Average lease terms going up", [], body="lease renewal costs rising")
    r = _create_research(client)

    res = client.post(f"/api/researches/{r['id']}/archive")
    assert res.status_code == 200
    hits = res.get_json()["research"]["hits"]
    matched_titles = [h["signal"]["title"] for h in hits]
    assert "Average lease terms going up" in matched_titles
    reasons = [h["match_reason"] for h in hits if h["signal"]["title"] == "Average lease terms going up"]
    assert any("keyword:lease" in r for r in reasons)


def test_archive_combined_score(client):
    _create_signal(client, "Rent going up in Irvine", ["housing"], body="monthly rent increase")
    r = _create_research(client)

    res = client.post(f"/api/researches/{r['id']}/archive")
    hits = res.get_json()["research"]["hits"]
    rent_hit = next(h for h in hits if h["signal"]["title"] == "Rent going up in Irvine")
    assert rent_hit["score"] > 0.5


def test_archive_replaces_old_hits(client):
    sid = _create_signal(client, "Old housing signal", ["housing"])
    r = _create_research(client)

    res1 = client.post(f"/api/researches/{r['id']}/archive")
    assert res1.get_json()["matched"] >= 1

    res2 = client.post(f"/api/researches/{r['id']}/archive")
    assert res2.status_code == 200
    hit_signal_ids = [h["signal_id"] for h in res2.get_json()["research"]["hits"]]
    assert hit_signal_ids.count(sid) <= 1


def test_archive_sets_status_active(client):
    _create_signal(client, "Housing data", ["housing"])
    r = _create_research(client)
    assert r["status"] == "draft"

    res = client.post(f"/api/researches/{r['id']}/archive")
    assert res.get_json()["research"]["status"] == "active"


def test_archive_not_found(client):
    res = client.post("/api/researches/9999/archive")
    assert res.status_code == 404


def test_archive_no_criteria(client):
    r = _create_research(client, keywords=[], categories=[])
    res = client.post(f"/api/researches/{r['id']}/archive")
    assert res.status_code == 400
    assert "category or keyword" in res.get_json()["error"].lower()


def test_detail_includes_hits(client):
    _create_signal(client, "Housing complaint", ["housing"])
    r = _create_research(client)
    client.post(f"/api/researches/{r['id']}/archive")

    res = client.get(f"/api/researches/{r['id']}")
    assert res.status_code == 200
    data = res.get_json()["research"]
    assert "hits" in data
    assert data["hit_count"] >= 1
