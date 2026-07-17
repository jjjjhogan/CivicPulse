"""Scrape job API."""

from __future__ import annotations

import json

from flask import Blueprint, jsonify, request

from backend.auth import get_current_user, login_required
from backend.db import get_session
from backend.jobs import build_command, is_job_running, normalize_source, start_job
from backend.models import ScrapeJob

bp = Blueprint("jobs", __name__)


def _parse_json_payload(raw) -> dict:
    if raw is None:
        raise ValueError("JSON payload is required.")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            raise ValueError("JSON payload is empty.")
        parsed = json.loads(text)
        if not isinstance(parsed, dict):
            raise ValueError("JSON payload must be an object.")
        return parsed
    raise ValueError("JSON payload must be an object or JSON string.")


def _extract_import_payload() -> dict:
    if request.files:
        upload = request.files.get("file") or next(iter(request.files.values()), None)
        if upload and upload.filename:
            text = upload.read().decode("utf-8", errors="replace")
            return _parse_json_payload(text)

    body = request.get_json(silent=True)
    if body is None:
        raw_text = (request.get_data(as_text=True) or "").strip()
        if not raw_text:
            raise ValueError("Paste JSON or upload a .json file.")
        return _parse_json_payload(raw_text)

    if not isinstance(body, dict):
        raise ValueError("Request body must be a JSON object.")

    if "payload" in body:
        return _parse_json_payload(body["payload"])
    if "data" in body and isinstance(body["data"], (dict, str)):
        return _parse_json_payload(body["data"])
    if "settings" in body and isinstance(body["settings"], dict):
        settings = body["settings"]
        if "payload" in settings:
            return _parse_json_payload(settings["payload"])
    return body


def _create_and_start_job(*, source: str, settings: dict):
    source = normalize_source(source)
    try:
        cmd = build_command(source, settings)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except json.JSONDecodeError as exc:
        return jsonify({"error": f"Invalid JSON payload: {exc}"}), 400

    if is_job_running():
        return jsonify({"error": "A scrape is already running."}), 409

    user = get_current_user()
    db = get_session()
    job = ScrapeJob(
        source=source,
        status="pending",
        settings=settings or {},
        user_id=user.id if user else None,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    if not start_job(job.id, cmd):
        job.status = "failed"
        job.error = "A scrape is already running."
        db.commit()
        return jsonify({"error": "A scrape is already running."}), 409

    db.refresh(job)
    return jsonify({"id": job.id, "status": job.status, "command": job.command}), 202


@bp.post("/api/jobs")
@login_required
def create_job():
    body = request.get_json(silent=True)
    if request.files:
        source = (request.form.get("source") or "").strip()
        if not source:
            return jsonify({"error": "source is required."}), 400
        try:
            payload = _extract_import_payload()
        except (ValueError, json.JSONDecodeError) as exc:
            return jsonify({"error": str(exc)}), 400
        return _create_and_start_job(source=source, settings={"payload": payload})

    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    source = (body.get("source") or "").strip()
    if not source:
        return jsonify({"error": "source is required."}), 400

    settings = body.get("settings")
    if settings is None:
        settings = {k: v for k, v in body.items() if k != "source"}
    if not isinstance(settings, dict):
        return jsonify({"error": "settings must be a JSON object."}), 400

    if source in {"reddit", "twitter"} and "payload" not in settings:
        if "payload" in body:
            try:
                settings = {**settings, "payload": _parse_json_payload(body["payload"])}
            except (ValueError, json.JSONDecodeError) as exc:
                return jsonify({"error": str(exc)}), 400

    return _create_and_start_job(source=source, settings=settings)


@bp.get("/api/jobs/<int:job_id>")
@login_required
def get_job(job_id: int):
    db = get_session()
    job = db.get(ScrapeJob, job_id)
    if job is None:
        return jsonify({"error": "Job not found."}), 404
    return jsonify(job.to_dict())


@bp.get("/api/scrape/status")
@login_required
def scrape_status_compat():
    """Legacy single-slot status for older clients; prefers the active/latest job."""
    db = get_session()
    running = (
        db.query(ScrapeJob)
        .filter(ScrapeJob.status == "running")
        .order_by(ScrapeJob.id.desc())
        .first()
    )
    job = running or db.query(ScrapeJob).order_by(ScrapeJob.id.desc()).first()
    if job is None:
        return jsonify(
            {
                "status": "idle",
                "source": None,
                "started_at": None,
                "finished_at": None,
                "exit_code": None,
                "command": None,
                "log": "",
                "error": None,
            }
        )
    payload = job.to_dict()
    # Match previous shape where timestamps were epoch seconds.
    for key in ("started_at", "finished_at"):
        if getattr(job, key) is not None:
            payload[key] = getattr(job, key).timestamp()
    return jsonify(payload)


@bp.post("/api/scrape/<source>")
@login_required
def scrape_source_compat(source: str):
    """Legacy scrape endpoints — create a job under the hood."""
    source = normalize_source(source)

    if source in {"reddit", "twitter"}:
        try:
            payload = _extract_import_payload()
        except (ValueError, json.JSONDecodeError) as exc:
            return jsonify({"error": str(exc)}), 400
        return _create_and_start_job(source=source, settings={"payload": payload})

    body = request.get_json(silent=True) or {}
    if not isinstance(body, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400
    return _create_and_start_job(source=source, settings=body)
