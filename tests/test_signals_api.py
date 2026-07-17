"""Signals API after DB import."""


def test_signals_from_db(client, imported_signals):
    res = client.get("/api/signals")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] == imported_signals
    assert len(data["signals"]) == imported_signals
    for row in data["signals"]:
        assert "source" in row
        assert "title" in row
        assert isinstance(row.get("categories"), list)


def test_config_endpoint(client):
    res = client.get("/api/config")
    assert res.status_code == 200
    data = res.get_json()
    assert "categories" in data
    assert "tiktok_defaults" in data
    assert "news_defaults" in data
    assert "news_outlets" in data
