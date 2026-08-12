"""WSGI entry point for gunicorn on Render."""

from backend.app import create_app

app = create_app()
