"""Opaque keyset cursors for signal list pagination."""

from __future__ import annotations

import base64
import json
from typing import Any


def encode_cursor(created_at: Any, signal_id: Any) -> str:
    payload = json.dumps(
        {"c": "" if created_at is None else str(created_at), "i": str(signal_id)},
        separators=(",", ":"),
    )
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii").rstrip("=")


def decode_cursor(cursor: str) -> tuple[str, str]:
    raw = (cursor or "").strip()
    if not raw:
        raise ValueError("empty cursor")
    pad = "=" * (-len(raw) % 4)
    data = json.loads(base64.urlsafe_b64decode(raw + pad).decode("utf-8"))
    created_at = data.get("c")
    signal_id = data.get("i")
    if created_at is None or signal_id is None:
        raise ValueError("invalid cursor")
    return str(created_at), str(signal_id)
