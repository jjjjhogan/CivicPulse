"""Firestore client initialization.

Credential lookup order:
  1. GOOGLE_CREDENTIALS_JSON — raw JSON string (for Render / hosted envs)
  2. GOOGLE_APPLICATION_CREDENTIALS — local file path (for dev)

Both require FIREBASE_PROJECT_ID or GOOGLE_CLOUD_PROJECT.

Never import this module at the top of app.py — it is loaded lazily
when DATA_BACKEND=firestore so the SQLite-only path stays dependency-free.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

_app: firebase_admin.App | None = None
_db = None


def _project_id() -> str | None:
    return (
        os.environ.get("FIREBASE_PROJECT_ID")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or None
    )


def _build_credential():
    """Return a firebase_admin Credential from env vars."""
    raw_json = (os.environ.get("GOOGLE_CREDENTIALS_JSON") or "").strip()
    if raw_json:
        info = json.loads(raw_json)
        return credentials.Certificate(info)

    cred_path = (os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "").strip()
    if not cred_path:
        raise RuntimeError(
            "Firestore requires GOOGLE_CREDENTIALS_JSON (raw JSON) or "
            "GOOGLE_APPLICATION_CREDENTIALS (file path)."
        )
    path = Path(cred_path)
    if not path.is_file():
        raise RuntimeError(f"Service-account file not found: {path}")
    return credentials.Certificate(str(path))


def get_firestore_client():
    """Return a cached Firestore client, initializing on first call."""
    global _app, _db
    if _db is not None:
        return _db

    project_id = _project_id()
    if not project_id:
        raise RuntimeError(
            "Firestore requires FIREBASE_PROJECT_ID (or GOOGLE_CLOUD_PROJECT)."
        )
    cred = _build_credential()
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
