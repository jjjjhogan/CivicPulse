"""Auth helpers: password hashing and session login gate."""

from __future__ import annotations

import os
from functools import wraps

from flask import jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from backend.store import get_user_store

SESSION_USER_KEY = "user_id"
SCRAPERS_FORBIDDEN_MSG = (
    "Scrapers run only on a local operator machine with a dev account."
)


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def get_current_user() -> dict | None:
    user_id = session.get(SESSION_USER_KEY)
    if not user_id:
        return None
    store = get_user_store()
    return store.get_user(user_id)


def login_user(user: dict) -> None:
    session.clear()
    session[SESSION_USER_KEY] = user["id"]
    session.permanent = True


def logout_user() -> None:
    session.clear()


def scrapers_host_ok() -> bool:
    """Scrapers are never available on Render's hosted instance."""
    return not bool(os.environ.get("RENDER"))


def scrapers_allowed(user: dict | None) -> bool:
    """True only off Render when the logged-in user has is_dev set."""
    if not scrapers_host_ok():
        return False
    return bool(user and user.get("is_dev"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            return jsonify({"error": "Authentication required."}), 401
        return view(*args, **kwargs)

    return wrapped
