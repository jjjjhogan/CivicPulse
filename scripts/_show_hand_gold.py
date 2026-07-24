"""Print next unlabeled hand-gold rows for interactive review."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "labels" / "review_batch_02_hand.json"


def main() -> None:
    start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    data = json.loads(PATH.read_text(encoding="utf-8"))
    rows = data["signals"]
    unlabeled = [r for r in rows if not r.get("verdict")]
    labeled = len(rows) - len(unlabeled)
    print(f"Progress: {labeled}/{len(rows)} labeled · showing up to {n} from offset {start}")
    print()
    chunk = unlabeled[start : start + n]
    for i, r in enumerate(chunk, start + 1):
        cats = ", ".join(r["categories"]) if r["categories"] else "[]"
        url = (r.get("url") or "").strip() or "(no url)"
        print(f"--- #{i} ---")
        print(f"id={r['id']}  source={r['source']}  method={r['method']}")
        print(f"assigned: {cats}")
        print(f"url: {url}")
        print(f"snippet: {r['snippet']}")
        print("verdict: (correct / wrong / none / partial)")
        print("note:")
        print()
    if chunk:
        ids = " ".join(str(r["id"]) for r in chunk)
        print(f"Open these in browser:  python scripts/_open_hand_gold.py {ids}")


if __name__ == "__main__":
    main()
