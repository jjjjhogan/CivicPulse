"""
CivicPulse dashboard server — serves the static UI and scrape/auth APIs.

Usage:
    python scripts/dashboard_server.py
    python scripts/dashboard_server.py --port 8080

Optional env (see .env.example): FLASK_SECRET_KEY, HOST, PORT, DATABASE_URL
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.app import create_app, main  # noqa: E402

app = create_app()

if __name__ == "__main__":
    main(app)
