"""Re-score gold sample against current signal classifications.

Loads the hand-labeled gold file and matches each signal to its current
version in data/signals/*.json (+ *_all.json) and the SQLite DB.
Reports correct/improved/unchanged/regressed counts vs. the human verdicts.
"""

from __future__ import annotations

import io
import json
import sqlite3
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
GOLD_PATH = ROOT / "data" / "labels" / "review_batch_02_hand.json"
SIGNALS_DIR = ROOT / "data" / "signals"
DB_PATH = ROOT / "data" / "civicpulse.db"
SOURCE_FILES = [
    "tiktok.json", "reddit.json", "twitter.json", "news.json",
    "reddit_all.json", "twitter_all.json",
]

SESSION_5_BASELINE = {"correct": 0.47, "matched": 79}


def _load_current_signals() -> tuple[list[dict], list[dict]]:
    """Load signals from JSON (primary) and DB (fallback), separately."""
    json_signals = []
    for name in SOURCE_FILES:
        path = SIGNALS_DIR / name
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            json_signals.extend(json.load(f))

    db_signals = []
    if DB_PATH.exists():
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        for row in conn.execute("SELECT * FROM signals"):
            db_signals.append({
                "source": row["source"],
                "title": row["title"] or "",
                "body": row["body"] or "",
                "url": row["url"] or "",
                "categories": json.loads(row["categories"]) if row["categories"] else [],
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            })
        conn.close()
    return json_signals, db_signals


def _normalize(text: str) -> str:
    return " ".join((text or "").split()).strip().rstrip("…").rstrip(".")


def _find_match(gold_sig: dict, current: list[dict]) -> dict | None:
    url = gold_sig.get("url", "")
    gold_title = _normalize(gold_sig.get("title", ""))
    gold_body = _normalize(gold_sig.get("body", ""))

    url_matches = [s for s in current if s.get("url", "") == url]
    if not url_matches:
        return None

    for s in url_matches:
        if _normalize(s.get("title", "")) == gold_title:
            return s

    for s in url_matches:
        cur_body = _normalize(s.get("body", ""))
        if gold_body and cur_body and gold_body == cur_body:
            return s

    for s in url_matches:
        cur_title = _normalize(s.get("title", ""))
        if cur_title and gold_title and (
            gold_title.startswith(cur_title) or cur_title.startswith(gold_title)
        ):
            return s

    if len(url_matches) == 1:
        return url_matches[0]

    return None


def rescore() -> None:
    with open(GOLD_PATH, encoding="utf-8") as f:
        gold = json.load(f)

    json_signals, db_signals = _load_current_signals()
    matched = 0
    unmatched_ids: list[int] = []

    verdicts = {"correct": 0, "wrong": 0, "none": 0, "partial": 0}
    now_correct = 0
    regressions: list[dict] = []
    improvements: list[dict] = []

    for sig in gold["signals"]:
        cur = _find_match(sig, json_signals) or _find_match(sig, db_signals)
        if cur is None:
            unmatched_ids.append(sig["id"])
            continue

        matched += 1
        verdict = sig["verdict"]
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        gold_cats = sorted(sig.get("categories") or [])
        cur_cats = sorted(cur.get("categories") or [])
        changed = gold_cats != cur_cats

        if verdict == "correct":
            if not changed:
                now_correct += 1
            else:
                regressions.append({
                    "id": sig["id"], "source": sig["source"],
                    "gold_cats": gold_cats, "cur_cats": cur_cats,
                    "snippet": sig["snippet"][:80],
                })
        elif verdict == "none":
            if not cur_cats:
                now_correct += 1
            elif changed and not cur_cats:
                now_correct += 1
                improvements.append({
                    "id": sig["id"], "verdict": verdict,
                    "gold_cats": gold_cats, "cur_cats": cur_cats,
                    "snippet": sig["snippet"][:80],
                })
        elif verdict == "wrong":
            if changed:
                improvements.append({
                    "id": sig["id"], "verdict": verdict,
                    "gold_cats": gold_cats, "cur_cats": cur_cats,
                    "snippet": sig["snippet"][:80],
                })
        elif verdict == "partial":
            if changed:
                improvements.append({
                    "id": sig["id"], "verdict": verdict,
                    "gold_cats": gold_cats, "cur_cats": cur_cats,
                    "snippet": sig["snippet"][:80],
                })

    unmatched = len(unmatched_ids)
    pct = round(now_correct / matched * 100, 1) if matched else 0
    print(f"\n{'='*60}")
    print(f"Gold re-score: {matched} matched, {unmatched} unmatched (of {len(gold['signals'])})")
    print(f"{'='*60}")
    print(f"\nVerdict distribution (matched only):")
    for v, n in sorted(verdicts.items()):
        print(f"  {v:>8}: {n}")
    print(f"\nNow correct: {now_correct}/{matched} ({pct}%)")
    s5 = SESSION_5_BASELINE
    print(f"Session 5 baseline: {s5['correct']:.0%} on {s5['matched']} matched")
    print(f"Delta: {pct - s5['correct']*100:+.1f}pp")

    if regressions:
        print(f"\nREGRESSIONS ({len(regressions)}):")
        for r in regressions:
            print(f"  id={r['id']} {r['source']}: {r['gold_cats']} -> {r['cur_cats']}")
            print(f"    {r['snippet']}")

    if improvements:
        print(f"\nIMPROVEMENTS ({len(improvements)}):")
        for imp in improvements:
            print(f"  id={imp['id']} [{imp['verdict']}]: {imp['gold_cats']} -> {imp['cur_cats']}")
            print(f"    {imp['snippet']}")

    if unmatched_ids:
        print(f"\nUnmatched IDs: {unmatched_ids}")

    print()


if __name__ == "__main__":
    rescore()
