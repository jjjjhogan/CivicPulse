"""Auth API: signup, login, logout, me."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.auth import (
    get_current_user,
    hash_password,
    login_user,
    logout_user,
    scrapers_allowed,
    scrapers_host_ok,
    verify_password,
)
from backend.store import get_user_store, public_user

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _is_valid_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1] and " " not in email


@bp.get("/me")
def me():
    user = get_current_user()
    if user is None:
        return jsonify({
            "authenticated": False,
            "user": None,
            "scrapers_allowed": False,
            "scrapers_host_ok": scrapers_host_ok(),
        })
    return jsonify({
        "authenticated": True,
        "user": public_user(user),
        "scrapers_allowed": scrapers_allowed(user),
        "scrapers_host_ok": scrapers_host_ok(),
    })


@bp.post("/signup")
def signup():
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    name = (body.get("name") or "").strip()
    email = _normalize_email(body.get("email") or "")
    password = body.get("password") or ""

    if not name:
        return jsonify({"error": "Enter your name."}), 400
    if not _is_valid_email(email):
        return jsonify({"error": "Enter a valid email address."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    store = get_user_store()
    if store.get_user_by_email(email) is not None:
        return jsonify({"error": "An account with that email already exists — log in instead."}), 409

    user = store.create_user(name=name, email=email, password_hash=hash_password(password))
    login_user(user)
    return jsonify({"ok": True, "user": public_user(user)}), 201


@bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    email = _normalize_email(body.get("email") or "")
    password = body.get("password") or ""

    if not _is_valid_email(email):
        return jsonify({"error": "Enter a valid email address."}), 400
    if not password:
        return jsonify({"error": "Enter your password."}), 400

    store = get_user_store()
    user = store.get_user_by_email(email)
    if user is None or not verify_password(user["password_hash"], password):
        return jsonify({"error": "Wrong email or password. New here? Create an account below."}), 401

    login_user(user)
    return jsonify({"ok": True, "user": public_user(user)})


@bp.post("/logout")
def logout():
    logout_user()
    return jsonify({"ok": True})
