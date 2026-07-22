"""Resident reports + community votes API (SQLite)."""

from __future__ import annotations


def _sample_report(**overrides):
    payload = {
        "title": "Pothole on Culver",
        "body": "Large hole near the turn lane",
        "categories": ["potholes"],
        "metadata": {
            "lat": 33.6846,
            "lng": -117.8265,
            "address": "Culver Dr, Irvine, CA",
            "reporter_name": "Alex Resident",
            "reporter_email": "alex@example.com",
            "reporter_phone": "",
        },
    }
    payload.update(overrides)
    return payload


def test_create_and_list_report(client):
    res = client.post("/api/reports", json=_sample_report())
    assert res.status_code == 201, res.get_json()
    body = res.get_json()
    signal = body["signal"]
    assert signal["source"] == "resident"
    assert signal["title"] == "Pothole on Culver"
    assert signal["id"] >= 1
    assert signal["metadata"]["lat"] == 33.6846

    listed = client.get("/api/reports")
    assert listed.status_code == 200
    data = listed.get_json()
    assert data["count"] >= 1
    assert data["storage"] == "db"
    assert any(row["id"] == signal["id"] for row in data["signals"])

    # Included in main signals feed from SQLite.
    all_signals = client.get("/api/signals").get_json()
    assert all_signals["storage"] == "db"
    assert any(row["id"] == signal["id"] for row in all_signals["signals"])


def test_create_report_validation(client):
    res = client.post("/api/reports", json={"title": "x", "categories": []})
    assert res.status_code == 400


def test_votes_require_auth_to_cast(client):
    created = client.post("/api/reports", json=_sample_report()).get_json()
    signal_id = created["signal"]["id"]

    res = client.post(
        "/api/votes",
        json={"signal_id": signal_id, "choice": "up"},
    )
    assert res.status_code == 401


def test_vote_toggle(auth_client):
    created = auth_client.post("/api/reports", json=_sample_report()).get_json()
    signal_id = created["signal"]["id"]

    up = auth_client.post(
        "/api/votes",
        json={"signal_id": signal_id, "choice": "up"},
    )
    assert up.status_code == 200, up.get_json()
    data = up.get_json()
    assert data["up"] == 1
    assert data["down"] == 0
    assert data["mine"] == "up"

    # Toggle off
    again = auth_client.post(
        "/api/votes",
        json={"signal_id": signal_id, "choice": "up"},
    )
    assert again.status_code == 200
    data = again.get_json()
    assert data["up"] == 0
    assert data["mine"] is None

    # Switch down
    down = auth_client.post(
        "/api/votes",
        json={"signal_id": signal_id, "choice": "down"},
    )
    assert down.status_code == 200
    data = down.get_json()
    assert data["down"] == 1
    assert data["mine"] == "down"

    listing = auth_client.get("/api/votes")
    assert listing.status_code == 200
    votes = listing.get_json()["votes"]
    assert votes[str(signal_id)]["down"] == 1
    assert votes[str(signal_id)]["mine"] == "down"


def test_vote_on_nonexistent_signal(auth_client):
    res = auth_client.post(
        "/api/votes",
        json={"signal_id": 99999, "choice": "up"},
    )
    assert res.status_code == 404


def test_vote_invalid_choice(auth_client):
    created = auth_client.post("/api/reports", json=_sample_report()).get_json()
    signal_id = created["signal"]["id"]
    res = auth_client.post(
        "/api/votes",
        json={"signal_id": signal_id, "choice": "sideways"},
    )
    assert res.status_code == 400


def test_votes_list_without_auth(client):
    client.post("/api/reports", json=_sample_report())
    res = client.get("/api/votes")
    assert res.status_code == 200
    data = res.get_json()
    assert "votes" in data


def test_report_missing_location(client):
    payload = _sample_report()
    del payload["metadata"]["lat"]
    del payload["metadata"]["lng"]
    res = client.post("/api/reports", json=payload)
    assert res.status_code == 400


def test_report_missing_address(client):
    payload = _sample_report()
    payload["metadata"]["address"] = ""
    res = client.post("/api/reports", json=payload)
    assert res.status_code == 400
