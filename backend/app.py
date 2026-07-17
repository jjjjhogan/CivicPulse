"""Flask application factory for CivicPulse."""

from __future__ import annotations

import argparse
import os
import socket
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, abort, redirect, send_from_directory

from backend.db import configure_engine, init_db, remove_session
from backend.routes import register_blueprints

ROOT = Path(__file__).resolve().parent.parent


def create_app(test_config: dict | None = None) -> Flask:
    load_dotenv(ROOT / ".env")

    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "civicpulse-dev-only-change-me")
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=14)
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    if test_config:
        app.config.update(test_config)
        db_url = test_config.get("SQLALCHEMY_DATABASE_URI") or test_config.get("DATABASE_URL")
        if db_url:
            configure_engine(db_url)
        if test_config.get("SECRET_KEY"):
            app.secret_key = test_config["SECRET_KEY"]

    init_db()
    register_blueprints(app)

    @app.teardown_appcontext
    def _shutdown_session(exception=None):  # noqa: ARG001
        remove_session()

    @app.get("/dashboard")
    def dashboard_shortcut():
        return redirect("/dashboard.html")

    @app.route("/", defaults={"filename": "index.html"})
    @app.route("/<path:filename>")
    def static_files(filename: str):
        if filename.startswith("api/"):
            abort(404)
        path = ROOT / filename
        if not path.is_file():
            abort(404)
        return send_from_directory(ROOT, filename)

    return app


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CivicPulse dashboard server.")
    parser.add_argument(
        "--host",
        default=os.environ.get("HOST", "127.0.0.1"),
        help="Bind host (default: HOST env or 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", "8080")),
        help="Bind port (default: PORT env or 8080)",
    )
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main(app: Flask | None = None) -> None:
    args = parse_args()
    if _port_in_use(args.host, args.port):
        print(
            f"Port {args.port} is already in use on {args.host}. "
            "Stop the other process first, or run with --port 8081."
        )
        raise SystemExit(1)

    flask_app = app or create_app()
    base = f"http://{args.host}:{args.port}"
    print("CivicPulse server running:")
    print(f"  Dashboard: {base}/dashboard.html")
    print(f"  Landing:   {base}/")
    print(f"  Login:     {base}/login.html")
    flask_app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)
