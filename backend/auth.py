"""Auth helpers: password hashing and session login gate."""

from __future__ import annotations

from functools import wraps

from flask import jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash

from backend.db import get_session
from backend.models import User

SESSION_USER_KEY = "user_id"


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def get_current_user() -> User | None:
    user_id = session.get(SESSION_USER_KEY)
    if not user_id:
        return None
    db = get_session()
    return db.get(User, user_id)


def login_user(user: User) -> None:
    session.clear()
    session[SESSION_USER_KEY] = user.id
    session.permanent = True


def logout_user() -> None:
    session.clear()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if get_current_user() is None:
            return jsonify({"error": "Authentication required."}), 401
        return view(*args, **kwargs)

    return wrapped
