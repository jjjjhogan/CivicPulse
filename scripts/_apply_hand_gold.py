"""Apply human verdicts to review_batch_02_hand.{json,md}.

Usage:
  python scripts/_apply_hand_gold.py 103:correct:serenity no civic
  python scripts/_apply_hand_gold.py 1:none:reaction only 23:wrong:wasted!=sanitation

Does not invent labels — only records what you pass on the CLI.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "labels" / "review_batch_02_hand.json"
MD_PATH = ROOT / "data" / "labels" / "review_batch_02_hand.md"
VALID = {"correct", "wrong", "none", "partial"}


def rebuild_md(data: dict) -> None:
    rows = data["signals"]
    labeled = [r for r in rows if r.get("verdict") in VALID]
    counts = Counter(r["verdict"] for r in labeled)
    total = len(labeled)

    def pct(v: str) -> str:
        return f"{(counts[v] / total * 100):.0f}%" if total else ""

    lines: list[str] = [
        "# Phase A — Hand Gold Sample (Batch #02)",
        "",
        "**Date:** 2026-07-24",
        "**Branch:** `feature/phase-a-gold-hand-s4`",
        "**Reviewers:** Jack + coworker (human only)",
        f"**Signals in worksheet:** {len(rows)} (stratified live DB sample; storage={data.get('storage')})",
        f"**Labeled so far:** {total}/{len(rows)}",
        "",
        "> AI first-pass in `review_batch_01.md` is **draft/scaffold only**. "
        "Do **not** copy its verdicts. This file is the gold sample.",
        "",
        "## How to review",
        "",
        "- Open the **source URL** under each row (or `python scripts/_open_hand_gold.py <id>`) before deciding.",
        "- Verdicts: `correct` / `wrong` / `none` / `partial` + short note.",
        "",
        "## Verdict key",
        "",
        "- **correct** — assigned category/categories fit the signal content",
        "- **wrong** — category does not match what the signal is about",
        "- **none** — no civic issue content; should not be categorized (or empty cats is right)",
        "- **partial** — some categories correct, some wrong or missing",
        "",
        "## Summary (human)",
        "",
        "| Verdict | Count | % |",
        "|---------|-------|---|",
        f"| correct | {counts['correct']} | {pct('correct')} |",
        f"| wrong | {counts['wrong']} | {pct('wrong')} |",
        f"| none | {counts['none']} | {pct('none')} |",
        f"| partial | {counts['partial']} | {pct('partial')} |",
        f"| **total labeled** | {total} |  |",
        "",
    ]

    by_m: dict[str, Counter] = defaultdict(Counter)
    by_s: dict[str, Counter] = defaultdict(Counter)
    m_tot: Counter = Counter()
    s_tot: Counter = Counter()
    for r in labeled:
        by_m[r["method"]][r["verdict"]] += 1
        by_s[r["source"]][r["verdict"]] += 1
        m_tot[r["method"]] += 1
        s_tot[r["source"]] += 1

    lines += [
        "### By method (human)",
        "",
        "| Method | Total | Correct | Wrong | None | Partial |",
        "|--------|-------|---------|-------|------|---------|",
    ]
    for method, tot in sorted(m_tot.items(), key=lambda kv: -kv[1]):
        c = by_m[method]
        lines.append(
            f"| {method} | {tot} | {c['correct']} | {c['wrong']} | {c['none']} | {c['partial']} |"
        )
    if not m_tot:
        lines.append("| _(pending)_ |  |  |  |  |  |")

    lines += [
        "",
        "### By source (human)",
        "",
        "| Source | Total | Correct | Wrong | None | Partial |",
        "|--------|-------|---------|-------|------|---------|",
    ]
    for source, tot in sorted(s_tot.items(), key=lambda kv: -kv[1]):
        c = by_s[source]
        lines.append(
            f"| {source} | {tot} | {c['correct']} | {c['wrong']} | {c['none']} | {c['partial']} |"
        )
    if not s_tot:
        lines.append("| _(pending)_ |  |  |  |  |  |")

    lines += [
        "",
        "## Top failure modes (human)",
        "",
        "_Update after a solid batch — measurement only._",
        "",
        "---",
        "",
        "## Raw hand review",
        "",
        "Format: `id | source | method | assigned_categories | verdict | notes`",
        "",
    ]

    for src, group_iter in groupby(rows, key=lambda r: r["source"]):
        group = list(group_iter)
        done = sum(1 for r in group if r.get("verdict") in VALID)
        lines.append(f"### {src} ({done}/{len(group)} labeled)")
        lines.append("")
        for r in group:
            cats = ", ".join(r["categories"]) if r["categories"] else "[]"
            verdict = r.get("verdict") or ""
            note = r.get("note") or ""
            url = r.get("url") or ""
            lines.append(f"**id={r['id']}** · method=`{r['method']}` · cats=`{cats}`")
            if url:
                lines.append(f"- source: <{url}>")
            lines.append(f"> {r['snippet']}")
            lines.append(f"`{r['id']} | {r['source']} | {r['method']} | {cats} | {verdict} | {note}`")
            lines.append("")
        lines.append("")

    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) < 2:
        print("Pass updates as id:verdict:note …")
        sys.exit(1)

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    by_id = {r["id"]: r for r in data["signals"]}
    for arg in sys.argv[1:]:
        m = re.match(r"^(\d+):(correct|wrong|none|partial):(.*)$", arg, re.DOTALL)
        if not m:
            print(f"Bad arg (want id:verdict:note): {arg!r}")
            sys.exit(2)
        sid, verdict, note = int(m.group(1)), m.group(2), m.group(3).strip()
        if sid not in by_id:
            print(f"Unknown id {sid}")
            sys.exit(3)
        by_id[sid]["verdict"] = verdict
        by_id[sid]["note"] = note
        print(f"Recorded id={sid} → {verdict} ({note})")

    JSON_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    rebuild_md(data)
    labeled = sum(1 for r in data["signals"] if r.get("verdict") in VALID)
    print(f"Saved {JSON_PATH.name} + {MD_PATH.name} · {labeled}/{len(data['signals'])} labeled")


if __name__ == "__main__":
    main()
