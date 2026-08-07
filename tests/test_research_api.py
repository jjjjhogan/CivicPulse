"""Research API — create, list, detail."""

from __future__ import annotations


def _sample_research(**overrides):
    payload = {
        "title": "Housing prices in Irvine",
        "topic": "Track housing cost trends and resident complaints",
        "keywords": ["rent", "housing prices", "lease"],
        "categories": ["housing"],
        "notes": "Demo research for archive matching.",
    }
    payload.update(overrides)
    return payload


def test_create_research(client):
    res = client.post("/api/researches", json=_sample_research())
    assert res.status_code == 201, res.get_json()
    data = res.get_json()["research"]
    assert data["title"] == "Housing prices in Irvine"
    assert data["keywords"] == ["rent", "housing prices", "lease"]
    assert data["categories"] == ["housing"]
    assert data["status"] == "draft"
    assert data["id"] >= 1
    assert data["created_at"] is not None


def test_create_research_minimal(client):
    res = client.post("/api/researches", json={"title": "Quick test"})
    assert res.status_code == 201
    data = res.get_json()["research"]
    assert data["title"] == "Quick test"
    assert data["keywords"] == []
    assert data["categories"] == []


def test_create_research_missing_title(client):
    res = client.post("/api/researches", json={"topic": "no title"})
    assert res.status_code == 400
    assert "title" in res.get_json()["error"].lower()


def test_create_research_bad_body(client):
    res = client.post("/api/researches", data="not json")
    assert res.status_code == 400


def test_list_researches(client):
    client.post("/api/researches", json=_sample_research(title="First"))
    client.post("/api/researches", json=_sample_research(title="Second"))
    res = client.get("/api/researches")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == 2
    titles = [r["title"] for r in data["researches"]]
    assert titles[0] == "Second"
    assert titles[1] == "First"


def test_get_research_detail(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.get(f"/api/researches/{rid}")
    assert res.status_code == 200
    data = res.get_json()["research"]
    assert data["id"] == rid
    assert data["title"] == "Housing prices in Irvine"


def test_get_research_not_found(client):
    res = client.get("/api/researches/9999")
    assert res.status_code == 404
