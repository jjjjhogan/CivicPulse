"""Tests for the store abstraction (SQLite + Firestore mock)."""

from __future__ import annotations

from unittest.mock import MagicMock

from backend.db import SessionLocal
from backend.models import Signal
from backend.store_firestore import (
    FirestoreJobStore,
    FirestoreSignalStore,
    FirestoreUserStore,
    FirestoreVoteStore,
)
from backend.store_sqlite import (
    SQLiteJobStore,
    SQLiteSignalStore,
    SQLiteUserStore,
    SQLiteVoteStore,
)


def _insert_signal(db, **overrides):
    defaults = {
        "source": "news",
        "outlet": "Test Outlet",
        "title": "Test signal",
        "body": "Some body text",
        "url": "http://example.com/1",
        "categories": ["housing"],
        "published_utc": "2026-01-15",
        "extra": {},
    }
    defaults.update(overrides)
    sig = Signal(**defaults)
    db.add(sig)
    db.commit()
    db.refresh(sig)
    return sig


def _make_mock_doc(doc_id, data):
    doc = MagicMock()
    doc.id = doc_id
    doc.exists = True
    doc.to_dict.return_value = data
    return doc


# =====================================================================
# SQLite Signal Store
# =====================================================================


def test_sqlite_list_signals(app):
    db = SessionLocal()
    _insert_signal(db, title="Alpha")
    _insert_signal(db, title="Beta")
    db.close()

    with app.app_context():
        store = SQLiteSignalStore(SessionLocal())
        signals = store.list_signals()
    assert len(signals) == 2
    assert signals[0]["title"] == "Alpha"
    assert signals[1]["title"] == "Beta"


def test_sqlite_list_feed_signals(app):
    db = SessionLocal()
    _insert_signal(db, title="Feed item", outlet="OC Voice")
    db.close()

    with app.app_context():
        store = SQLiteSignalStore(SessionLocal())
        feed = store.list_feed_signals()
    assert len(feed) == 1
    assert feed[0]["title"] == "Feed item"
    assert "body" not in feed[0]


def test_sqlite_get_signal(app):
    db = SessionLocal()
    sig = _insert_signal(db, title="Lookup me")
    sig_id = sig.id
    db.close()

    with app.app_context():
        store = SQLiteSignalStore(SessionLocal())
        result = store.get_signal(sig_id)
    assert result is not None
    assert result["title"] == "Lookup me"


def test_sqlite_get_signal_not_found(app):
    with app.app_context():
        store = SQLiteSignalStore(SessionLocal())
        assert store.get_signal(99999) is None


def test_sqlite_create_signal(app):
    with app.app_context():
        store = SQLiteSignalStore(SessionLocal())
        sig = store.create_signal(
            source="resident",
            outlet="Report",
            title="New signal",
            body="body",
            url="",
            categories=["housing"],
            published_utc="2026-05-01",
            metadata={"lat": 33.0, "lng": -117.0},
        )
    assert sig["title"] == "New signal"
    assert sig["source"] == "resident"
    assert sig["id"] >= 1


def test_sqlite_list_signals_by_source(app):
    db = SessionLocal()
    _insert_signal(db, title="Resident one", source="resident")
    _insert_signal(db, title="News one", source="news")
    _insert_signal(db, title="Resident two", source="resident")
    db.close()

    with app.app_context():
        store = SQLiteSignalStore(SessionLocal())
        residents = store.list_signals_by_source("resident")
    assert len(residents) == 2
    assert all(r["source"] == "resident" for r in residents)


# =====================================================================
# SQLite User Store
# =====================================================================


def test_sqlite_create_and_get_user(app):
    with app.app_context():
        store = SQLiteUserStore(SessionLocal())
        user = store.create_user(name="Alice", email="alice@test.com", password_hash="hash123")
    assert user["name"] == "Alice"
    assert user["email"] == "alice@test.com"
    assert user["password_hash"] == "hash123"
    assert user["id"] >= 1

    with app.app_context():
        store2 = SQLiteUserStore(SessionLocal())
        found = store2.get_user(user["id"])
    assert found is not None
    assert found["name"] == "Alice"


def test_sqlite_get_user_by_email(app):
    with app.app_context():
        store = SQLiteUserStore(SessionLocal())
        store.create_user(name="Bob", email="bob@test.com", password_hash="pw")
        found = store.get_user_by_email("bob@test.com")
    assert found is not None
    assert found["name"] == "Bob"


def test_sqlite_get_user_not_found(app):
    with app.app_context():
        store = SQLiteUserStore(SessionLocal())
        assert store.get_user(99999) is None
        assert store.get_user_by_email("nobody@test.com") is None


# =====================================================================
# SQLite Job Store
# =====================================================================


def test_sqlite_create_and_list_jobs(app):
    with app.app_context():
        store = SQLiteJobStore(SessionLocal())
        job = store.create_job(source="tiktok", settings={"mode": "tags"})
    assert job["source"] == "tiktok"
    assert job["status"] == "pending"
    assert job["id"] >= 1

    with app.app_context():
        store2 = SQLiteJobStore(SessionLocal())
        jobs = store2.list_jobs(limit=10)
    assert len(jobs) == 1
    assert jobs[0]["id"] == job["id"]


def test_sqlite_update_job(app):
    with app.app_context():
        store = SQLiteJobStore(SessionLocal())
        job = store.create_job(source="news", settings={})
        store.update_job(job["id"], status="running", command="py scrape.py")
        refreshed = store.get_job(job["id"])
    assert refreshed["status"] == "running"
    assert refreshed["command"] == "py scrape.py"


def test_sqlite_get_running_job(app):
    with app.app_context():
        store = SQLiteJobStore(SessionLocal())
        assert store.get_running_job() is None
        j = store.create_job(source="tiktok", settings={})
        store.update_job(j["id"], status="running")
        running = store.get_running_job()
    assert running is not None
    assert running["status"] == "running"


# =====================================================================
# SQLite Vote Store
# =====================================================================


def test_sqlite_cast_and_summarize_votes(app):
    db = SessionLocal()
    sig = _insert_signal(db, source="resident", title="Vote target")
    sig_id = sig.id
    db.close()

    with app.app_context():
        from backend.store_sqlite import SQLiteUserStore

        ustore = SQLiteUserStore(SessionLocal())
        user = ustore.create_user(name="Voter", email="voter@test.com", password_hash="pw")

    with app.app_context():
        vstore = SQLiteVoteStore(SessionLocal())
        vstore.cast_vote(signal_id=sig_id, user_id=user["id"], choice="up")
        summary = vstore.summarize_votes([sig_id], user_id=user["id"])
    assert summary[str(sig_id)]["up"] == 1
    assert summary[str(sig_id)]["mine"] == "up"


def test_sqlite_cast_vote_toggle(app):
    db = SessionLocal()
    sig = _insert_signal(db, source="resident", title="Toggle target")
    sig_id = sig.id
    db.close()

    with app.app_context():
        ustore = SQLiteUserStore(SessionLocal())
        user = ustore.create_user(name="Toggler", email="toggler@test.com", password_hash="pw")

    with app.app_context():
        vstore = SQLiteVoteStore(SessionLocal())
        vstore.cast_vote(signal_id=sig_id, user_id=user["id"], choice="up")
        vstore.cast_vote(signal_id=sig_id, user_id=user["id"], choice="up")
        summary = vstore.summarize_votes([sig_id], user_id=user["id"])
    assert summary[str(sig_id)]["up"] == 0
    assert summary[str(sig_id)]["mine"] is None


# =====================================================================
# Firestore Signal Store (mocked)
# =====================================================================


def test_firestore_list_signals():
    docs = [
        _make_mock_doc("abc", {
            "source": "tiktok", "outlet": "TikTok", "title": "FS signal 1",
            "body": "body1", "url": "http://fs.example/1",
            "categories": ["public_safety"], "published_utc": "2026-02-01",
            "metadata": {"tag": "test"}, "created_at": "2026-02-01T00:00:00Z",
        }),
        _make_mock_doc("def", {
            "source": "news", "outlet": "IS", "title": "FS signal 2",
            "body": "body2", "url": "http://fs.example/2",
            "categories": ["housing"], "published_utc": "2026-02-02",
            "metadata": {}, "created_at": "2026-02-02T00:00:00Z",
        }),
    ]
    mock_db = MagicMock()
    mock_db.collection.return_value.order_by.return_value.stream.return_value = iter(docs)

    store = FirestoreSignalStore(mock_db)
    signals = store.list_signals()
    assert len(signals) == 2
    assert signals[0]["id"] == "abc"
    assert signals[1]["title"] == "FS signal 2"


def test_firestore_list_feed_signals():
    docs = [_make_mock_doc("x1", {
        "outlet": "Voice of OC", "title": "Feed title",
        "categories": ["traffic_safety"], "published_utc": "2026-03-01",
        "created_at": "2026-03-01T00:00:00Z",
    })]
    mock_db = MagicMock()
    mock_db.collection.return_value.order_by.return_value.stream.return_value = iter(docs)

    store = FirestoreSignalStore(mock_db)
    feed = store.list_feed_signals()
    assert len(feed) == 1
    assert "body" not in feed[0]


def test_firestore_get_signal():
    doc = _make_mock_doc("sig123", {
        "source": "reddit", "outlet": "r/irvine", "title": "Found signal",
        "body": "details", "url": "http://reddit.com/x",
        "categories": ["housing"], "published_utc": "2026-04-01", "metadata": {},
    })
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreSignalStore(mock_db)
    result = store.get_signal("sig123")
    assert result is not None
    assert result["id"] == "sig123"


def test_firestore_get_signal_not_found():
    doc = MagicMock()
    doc.exists = False
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreSignalStore(mock_db)
    assert store.get_signal("missing") is None


# =====================================================================
# Firestore User Store (mocked)
# =====================================================================


def test_firestore_create_user():
    mock_db = MagicMock()
    mock_ref = MagicMock()
    mock_ref.id = "user_abc"
    mock_db.collection.return_value.add.return_value = (None, mock_ref)

    store = FirestoreUserStore(mock_db)
    user = store.create_user(name="Alice", email="alice@test.com", password_hash="hash")
    assert user["id"] == "user_abc"
    assert user["name"] == "Alice"
    assert user["email"] == "alice@test.com"


def test_firestore_get_user():
    doc = _make_mock_doc("u1", {
        "email": "bob@test.com", "name": "Bob", "password_hash": "pw",
    })
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreUserStore(mock_db)
    user = store.get_user("u1")
    assert user["id"] == "u1"
    assert user["name"] == "Bob"


def test_firestore_get_user_by_email():
    doc = _make_mock_doc("u2", {
        "email": "carol@test.com", "name": "Carol", "password_hash": "pw",
    })
    mock_db = MagicMock()
    mock_db.collection.return_value.where.return_value.limit.return_value.stream.return_value = iter([doc])

    store = FirestoreUserStore(mock_db)
    user = store.get_user_by_email("carol@test.com")
    assert user is not None
    assert user["name"] == "Carol"


def test_firestore_get_user_by_email_not_found():
    mock_db = MagicMock()
    mock_db.collection.return_value.where.return_value.limit.return_value.stream.return_value = iter([])

    store = FirestoreUserStore(mock_db)
    assert store.get_user_by_email("nobody@test.com") is None


# =====================================================================
# Firestore Job Store (mocked)
# =====================================================================


def test_firestore_create_job():
    mock_db = MagicMock()
    mock_ref = MagicMock()
    mock_ref.id = "job_xyz"
    mock_db.collection.return_value.add.return_value = (None, mock_ref)

    store = FirestoreJobStore(mock_db)
    job = store.create_job(source="tiktok", settings={"mode": "tags"})
    assert job["id"] == "job_xyz"
    assert job["source"] == "tiktok"
    assert job["status"] == "pending"


def test_firestore_get_job():
    doc = _make_mock_doc("j1", {
        "source": "news", "status": "completed", "settings": {},
        "command": "py scrape.py", "log": "ok", "error": None,
        "exit_code": 0, "user_id": None,
        "created_at": "2026-01-01T00:00:00Z",
        "started_at": "2026-01-01T00:01:00Z",
        "finished_at": "2026-01-01T00:02:00Z",
    })
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreJobStore(mock_db)
    job = store.get_job("j1")
    assert job["id"] == "j1"
    assert job["status"] == "completed"


def test_firestore_update_job():
    mock_db = MagicMock()
    store = FirestoreJobStore(mock_db)
    store.update_job("j1", status="running", command="py x.py")
    mock_db.collection.return_value.document.return_value.update.assert_called_once()


# =====================================================================
# Firestore Vote Store (mocked)
# =====================================================================


def test_firestore_cast_vote_new():
    doc = MagicMock()
    doc.exists = False
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreVoteStore(mock_db)
    store.cast_vote(signal_id="s1", user_id="u1", choice="up")
    mock_db.collection.return_value.document.return_value.set.assert_called_once()


def test_firestore_cast_vote_toggle():
    doc = MagicMock()
    doc.exists = True
    doc.to_dict.return_value = {"choice": "up"}
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreVoteStore(mock_db)
    store.cast_vote(signal_id="s1", user_id="u1", choice="up")
    mock_db.collection.return_value.document.return_value.delete.assert_called_once()


def test_firestore_cast_vote_change():
    doc = MagicMock()
    doc.exists = True
    doc.to_dict.return_value = {"choice": "up"}
    mock_db = MagicMock()
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    store = FirestoreVoteStore(mock_db)
    store.cast_vote(signal_id="s1", user_id="u1", choice="down")
    mock_db.collection.return_value.document.return_value.update.assert_called_once()


def test_firestore_summarize_votes():
    vote_docs = [
        _make_mock_doc("s1_u1", {"signal_id": "s1", "user_id": "u1", "choice": "up"}),
        _make_mock_doc("s1_u2", {"signal_id": "s1", "user_id": "u2", "choice": "down"}),
    ]
    mock_db = MagicMock()
    mock_db.collection.return_value.where.return_value.stream.return_value = iter(vote_docs)

    store = FirestoreVoteStore(mock_db)
    summary = store.summarize_votes(["s1"], user_id="u1")
    assert summary["s1"]["up"] == 1
    assert summary["s1"]["down"] == 1
    assert summary["s1"]["mine"] == "up"
