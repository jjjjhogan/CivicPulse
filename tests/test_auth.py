"""Auth API tests — signup / login / logout / me / gated jobs."""


def test_me_anonymous(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 200
    data = res.get_json()
    assert data["authenticated"] is False
    assert data["user"] is None
    assert data["scrapers_allowed"] is False
    assert data["scrapers_host_ok"] is True


def test_signup_and_me(client):
    res = client.post(
        "/api/auth/signup",
        json={"name": "Ada", "email": "ada@example.com", "password": "secret12"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["ok"] is True
    assert body["user"]["email"] == "ada@example.com"

    me = client.get("/api/auth/me").get_json()
    assert me["authenticated"] is True
    assert me["user"]["name"] == "Ada"
    assert me["user"]["is_dev"] is False
    assert me["scrapers_allowed"] is False
    assert me["scrapers_host_ok"] is True


def test_duplicate_signup(client):
    payload = {"name": "Ada", "email": "dup@example.com", "password": "secret12"}
    assert client.post("/api/auth/signup", json=payload).status_code == 201
    res = client.post("/api/auth/signup", json=payload)
    assert res.status_code == 409


def test_wrong_password(client):
    client.post(
        "/api/auth/signup",
        json={"name": "Bob", "email": "bob@example.com", "password": "secret12"},
    )
    client.post("/api/auth/logout")
    res = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "wrong-password"},
    )
    assert res.status_code == 401


def test_logout(client):
    client.post(
        "/api/auth/signup",
        json={"name": "Cara", "email": "cara@example.com", "password": "secret12"},
    )
    assert client.get("/api/auth/me").get_json()["authenticated"] is True
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").get_json()["authenticated"] is False


def test_jobs_require_auth(client):
    res = client.post(
        "/api/jobs",
        json={"source": "irvine-news", "settings": {"max_articles": 1}},
    )
    assert res.status_code == 401


def test_me_includes_is_dev_when_set(dev_client):
    me = dev_client.get("/api/auth/me").get_json()
    assert me["authenticated"] is True
    assert me["user"]["is_dev"] is True
    assert me["scrapers_allowed"] is True
    assert me["scrapers_host_ok"] is True


def test_me_scrapers_blocked_on_render(dev_client, monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    me = dev_client.get("/api/auth/me").get_json()
    assert me["user"]["is_dev"] is True
    assert me["scrapers_host_ok"] is False
    assert me["scrapers_allowed"] is False
