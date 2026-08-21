"""Research API — create, list, detail, update, delete."""

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


def test_create_research_with_compose_fields(client):
    payload = _sample_research(
        extract=["sentiment", "clustering"],
        listen_sources=["twitter", "news311"],
        languages=["en", "es"],
        time_window="90d",
        geo_radius="5mi",
    )
    res = client.post("/api/researches", json=payload)
    assert res.status_code == 201
    data = res.get_json()["research"]
    assert data["extract"] == ["sentiment", "clustering"]
    assert data["listen_sources"] == ["twitter", "news311"]
    assert data["languages"] == ["en", "es"]
    assert data["time_window"] == "90d"
    assert data["geo_radius"] == "5mi"


def test_create_research_minimal(client):
    res = client.post("/api/researches", json={"title": "Quick test"})
    assert res.status_code == 201
    data = res.get_json()["research"]
    assert data["title"] == "Quick test"
    assert data["keywords"] == []
    assert data["categories"] == []
    assert data["extract"] == []
    assert data["listen_sources"] == []
    assert data["languages"] == []
    assert data["time_window"] == "30d"
    assert data["geo_radius"] == "irvine"


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


def test_update_research(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.patch(
        f"/api/researches/{rid}",
        json={"keywords": ["mortgage", "rent"], "status": "active"},
    )
    assert res.status_code == 200
    data = res.get_json()["research"]
    assert data["keywords"] == ["mortgage", "rent"]
    assert data["status"] == "active"


def test_update_research_compose_fields(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.patch(
        f"/api/researches/{rid}",
        json={
            "extract": ["sentiment", "policy"],
            "listen_sources": ["tiktok"],
            "languages": ["en"],
            "time_window": "7d",
            "geo_radius": "10mi",
        },
    )
    assert res.status_code == 200
    data = res.get_json()["research"]
    assert data["extract"] == ["sentiment", "policy"]
    assert data["listen_sources"] == ["tiktok"]
    assert data["languages"] == ["en"]
    assert data["time_window"] == "7d"
    assert data["geo_radius"] == "10mi"


def test_update_research_invalid_status(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.patch(f"/api/researches/{rid}", json={"status": "bogus"})
    assert res.status_code == 400
    assert "status" in res.get_json()["error"].lower()


def test_update_research_empty_title_rejected(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.patch(f"/api/researches/{rid}", json={"title": ""})
    assert res.status_code == 400


def test_update_research_not_found(client):
    res = client.patch("/api/researches/9999", json={"status": "active"})
    assert res.status_code == 404


def test_delete_research(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.delete(f"/api/researches/{rid}")
    assert res.status_code == 200
    assert res.get_json()["deleted"] is True
    assert client.get(f"/api/researches/{rid}").status_code == 404


def test_delete_research_not_found(client):
    res = client.delete("/api/researches/9999")
    assert res.status_code == 404


def test_list_includes_hit_count(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    listing = client.get("/api/researches").get_json()
    r = next(x for x in listing["researches"] if x["id"] == rid)
    assert "hit_count" in r
    assert r["hit_count"] == 0


def test_list_research_jobs_empty(client):
    created = client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]
    res = client.get(f"/api/researches/{rid}/jobs")
    assert res.status_code == 200
    assert res.get_json()["jobs"] == []


def test_list_research_jobs_not_found(client):
    res = client.get("/api/researches/9999/jobs")
    assert res.status_code == 404


def test_launch_research(client):
    created = client.post("/api/researches", json=_sample_research(
        listen_sources=["news311", "tiktok", "twitter"],
        extract=["sentiment", "clustering"],
    )).get_json()
    rid = created["research"]["id"]
    res = client.post(f"/api/researches/{rid}/launch")
    assert res.status_code == 200
    data = res.get_json()
    assert data["research"]["status"] == "active"
    assert "sentiment" in data["extract_sections"]
    assert "clustering" in data["extract_sections"]


def test_launch_research_not_found(client):
    res = client.post("/api/researches/9999/launch")
    assert res.status_code == 404


def test_launch_filters_by_listen_sources(client):
    created = client.post("/api/researches", json=_sample_research(
        listen_sources=["youtube"],
    )).get_json()
    rid = created["research"]["id"]
    res = client.post(f"/api/researches/{rid}/launch")
    assert res.status_code == 200
    assert res.get_json()["hit_count"] == 0


def test_draft_does_not_launch(client):
    created = client.post("/api/researches", json=_sample_research(
        listen_sources=["news311"],
    )).get_json()
    data = created["research"]
    assert data["status"] == "draft"
    assert data["listen_sources"] == ["news311"]


def test_summary_gated_by_extract(client):
    created = client.post("/api/researches", json=_sample_research(
        extract=["sentiment", "clustering"],
    )).get_json()
    rid = created["research"]["id"]
    res = client.get(f"/api/researches/{rid}/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert "sentiment" in data["sections"]
    assert "clustering" in data["sections"]
    assert "demographics" not in data["sections"]
    assert "policy" not in data["sections"]
    assert data["extract"] == ["sentiment", "clustering"]


def test_summary_empty_extract(client):
    created = client.post("/api/researches", json=_sample_research(
        extract=[],
    )).get_json()
    rid = created["research"]["id"]
    res = client.get(f"/api/researches/{rid}/summary")
    assert res.status_code == 200
    data = res.get_json()
    assert data["sections"] == {}


def test_summary_not_found(client):
    res = client.get("/api/researches/9999/summary")
    assert res.status_code == 404


def test_preview_metrics(client):
    res = client.post("/api/researches/preview", json={
        "listen_sources": ["news311", "tiktok"],
        "time_window": "30d",
    })
    assert res.status_code == 200
    data = res.get_json()
    assert "archive_count" in data
    assert "estimated_voices" in data
    assert "coverage_pct" in data
    assert data["sources_on"] == 2
    assert data["label"] == "estimate"


def test_suggest_expansions(client):
    res = client.post("/api/suggest/expansions", json={"title": "Affordable housing supply and rent burden"})
    assert res.status_code == 200
    data = res.get_json()
    assert "voice_chips" in data
    assert "civic_chips" in data
    assert "categories" in data
    assert "housing" in data["categories"]
    assert len(data["voice_chips"]) > 0


def test_suggest_expansions_short_title(client):
    res = client.post("/api/suggest/expansions", json={"title": "Hi"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["voice_chips"] == []
    assert data["civic_chips"] == []
    assert data["categories"] == []


def test_create_job_with_research_id(dev_client, monkeypatch):
    import subprocess

    monkeypatch.setattr(
        "backend.jobs.subprocess.run",
        lambda *a, **k: subprocess.CompletedProcess(
            args=a[0] if a else [], returncode=0, stdout="ok\n", stderr=""
        ),
    )
    monkeypatch.setattr("backend.jobs.threading.Thread", lambda target, args=(), kwargs=None, daemon=None: type("T", (), {"start": lambda self: target(*args, **(kwargs or {}))})())
    monkeypatch.setattr(
        "backend.signals_import.sync_signals_after_scrape",
        lambda source=None: {"inserted": 0, "updated": 0},
    )

    created = dev_client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]

    res = dev_client.post(
        "/api/jobs",
        json={"source": "irvine-news", "research_id": rid},
    )
    assert res.status_code == 202
    job_id = res.get_json()["id"]

    job = dev_client.get(f"/api/jobs/{job_id}").get_json()
    assert job["research_id"] == rid

    jobs_for_research = dev_client.get(f"/api/researches/{rid}/jobs").get_json()
    assert len(jobs_for_research["jobs"]) == 1
    assert jobs_for_research["jobs"][0]["id"] == job_id


def test_tiktok_job_returns_501_when_unavailable(dev_client, monkeypatch):
    monkeypatch.setattr("backend.routes.jobs.selenium_available", lambda: False)
    created = dev_client.post("/api/researches", json=_sample_research()).get_json()
    rid = created["research"]["id"]

    res = dev_client.post(
        "/api/jobs",
        json={"source": "tiktok", "research_id": rid},
    )
    assert res.status_code == 501
    data = res.get_json()
    assert "desktop" in data["error"].lower()


def test_tiktok_job_passes_settings(dev_client, monkeypatch):
    import subprocess

    captured = {}

    def fake_run(*a, **k):
        captured["cmd"] = a[0] if a else k.get("args", [])
        return subprocess.CompletedProcess(args=captured["cmd"], returncode=0, stdout="ok\n", stderr="")

    monkeypatch.setattr("backend.routes.jobs.selenium_available", lambda: True)
    monkeypatch.setattr("backend.jobs.subprocess.run", fake_run)
    monkeypatch.setattr("backend.jobs.threading.Thread", lambda target, args=(), kwargs=None, daemon=None: type("T", (), {"start": lambda self: target(*args, **(kwargs or {}))})())
    monkeypatch.setattr(
        "backend.signals_import.sync_signals_after_scrape",
        lambda source=None: {"inserted": 0, "updated": 0},
    )

    res = dev_client.post(
        "/api/jobs",
        json={
            "source": "tiktok",
            "settings": {"tag_urls": ["https://www.tiktok.com/tag/irvine"]},
        },
    )
    assert res.status_code == 202
    cmd = captured.get("cmd", [])
    assert "--tag-url" in cmd
    assert "https://www.tiktok.com/tag/irvine" in cmd
