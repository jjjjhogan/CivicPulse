"""Firestore client initialization.

Uses the Firebase Admin SDK. Connects to the emulator when
FIRESTORE_EMULATOR_HOST is set, otherwise uses application-default
credentials or a service-account JSON pointed to by
GOOGLE_APPLICATION_CREDENTIALS.

Never import this module at the top of app.py — it is loaded lazily
when DATA_BACKEND=firestore so the SQLite-only path stays dependency-free.
"""

from __future__ import annotations

import os

import firebase_admin
from firebase_admin import credentials, firestore

_app: firebase_admin.App | None = None
_db = None


def get_firestore_client():
    """Return a cached Firestore client, initializing on first call."""
    global _app, _db
    if _db is not None:
        return _db

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "civicpulse-local")
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

    if cred_path:
        cred = credentials.Certificate(cred_path)
    else:
        cred = credentials.ApplicationDefault()

    try:
        _app = firebase_admin.initialize_app(cred, {"projectId": project_id})
    except ValueError:
        _app = firebase_admin.get_app()

    _db = firestore.client(_app)
    return _db


def reset_firestore_client() -> None:
    """Tear down the cached client (for tests)."""
    global _app, _db
    _db = None
    if _app is not None:
        try:
            firebase_admin.delete_app(_app)
        except ValueError:
            pass
        _app = None
