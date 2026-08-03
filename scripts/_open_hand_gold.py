"""Open source URL(s) for signal id(s) in the default browser.

Looks up `review_batch_02_hand.json` first, then falls back to live
`GET /api/signals` (same DB id schema as review_batch_01).

Usage:
  python scripts/_open_hand_gold.py 1
  python scripts/_open_hand_gold.py 1 23 116
  python scripts/_open_hand_gold.py --batch 0 5   # first 5 unlabeled in hand worksheet
  python scripts/_open_hand_gold.py --answers     # all ids from batch_01_answers.txt
"""

from __future__ import annotations

import json
import sys
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HAND_PATH = ROOT / "data" / "labels" / "review_batch_02_hand.json"
ANSWERS_PATH = ROOT / "data" / "labels" / "batch_01_answers.txt"
API = "http://127.0.0.1:8080/api/signals"


def load_live() -> dict[int, dict]:
    with urllib.request.urlopen(API, timeout=30) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return {int(s["id"]): s for s in payload["signals"]}


def resolve(sid: int, hand: dict[int, dict], live: dict[int, dict] | None) -> tuple[str, str, str]:
    """Return (source, url, where_found)."""
    if sid in hand and (hand[sid].get("url") or "").strip():
        row = hand[sid]
        return row.get("source") or "?", row["url"].strip(), "hand"
    if live is None:
        live = load_live()
    if sid in live and (live[sid].get("url") or "").strip():
        row = live[sid]
        return row.get("source") or "?", row["url"].strip(), "live"
    return "?", "", "missing"


def main() -> None:
    data = json.loads(HAND_PATH.read_text(encoding="utf-8"))
    hand = {int(r["id"]): r for r in data["signals"]}
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    ids: list[int] = []
    if args[0] == "--batch":
        start = int(args[1]) if len(args) > 1 else 0
        n = int(args[2]) if len(args) > 2 else 5
        unlabeled = [r for r in data["signals"] if not r.get("verdict")]
        ids = [int(r["id"]) for r in unlabeled[start : start + n]]
    elif args[0] == "--answers":
        for line in ANSWERS_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ids.append(int(line.split(":", 1)[0]))
    else:
        ids = [int(a) for a in args]

    live: dict[int, dict] | None = None
    # Prefetch live if any id is outside the hand sample
    if any(sid not in hand or not (hand[sid].get("url") or "").strip() for sid in ids):
        try:
            live = load_live()
        except Exception as exc:  # noqa: BLE001
            print(f"Live API unavailable ({exc}); hand worksheet only.")
            live = {}

    for sid in ids:
        source, url, where = resolve(sid, hand, live)
        if not url:
            print(f"id={sid}: no url (not in hand sample or live DB)")
            continue
        print(f"Opening id={sid} ({source}, via {where}): {url}")
        webbrowser.open(url)


if __name__ == "__main__":
    main()
