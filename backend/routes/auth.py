"""Auth API: signup, login, logout, me."""

from __future__ import annotations

from flask import Blueprint, jsonify, request

from backend.auth import (
    get_current_user,
    hash_password,
    login_user,
    logout_user,
    verify_password,
)
from backend.db import get_session
from backend.models import User

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def _is_valid_email(email: str) -> bool:
    return "@" in email and "." in email.split("@")[-1] and " " not in email


@bp.get("/me")
def me():
    user = get_current_user()
    if user is None:
        return jsonify({"authenticated": False, "user": None})
    return jsonify({"authenticated": True, "user": user.to_public_dict()})


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

    db = get_session()
    if db.query(User).filter_by(email=email).first() is not None:
        return jsonify({"error": "An account with that email already exists — log in instead."}), 409

    user = User(name=name, email=email, password_hash=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    login_user(user)
    return jsonify({"ok": True, "user": user.to_public_dict()}), 201


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

    db = get_session()
    user = db.query(User).filter_by(email=email).first()
    if user is None or not verify_password(user.password_hash, password):
        return jsonify({"error": "Wrong email or password. New here? Create an account below."}), 401

    login_user(user)
    return jsonify({"ok": True, "user": user.to_public_dict()})


@bp.post("/logout")
def logout():
    logout_user()
    return jsonify({"ok": True})
