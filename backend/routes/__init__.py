"""HTTP route blueprints."""

from __future__ import annotations

from flask import Flask

from backend.routes.auth import bp as auth_bp
from backend.routes.jobs import bp as jobs_bp
from backend.routes.reports import bp as reports_bp
from backend.routes.signals import bp as signals_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(signals_bp)
    app.register_blueprint(reports_bp)
