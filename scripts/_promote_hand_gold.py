"""Promote part A/B human answers into review_batch_02_hand gold + draft clusters."""

from __future__ import annotations

import json
import re
import urllib.request
from collections import Counter, defaultdict
from itertools import groupby
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PARTS = [
    ROOT / "data" / "labels" / "batch_01_answers_part_a.txt",
    ROOT / "data" / "labels" / "batch_01_answers_part_b.txt",
]
OUT_JSON = ROOT / "data" / "labels" / "review_batch_02_hand.json"
OUT_MD = ROOT / "data" / "labels" / "review_batch_02_hand.md"
COMBINED = ROOT / "data" / "labels" / "batch_01_answers.txt"
CLUSTERS = ROOT / "data" / "labels" / "failure_clusters_draft.md"
API = "http://127.0.0.1:8080/api/signals"
VALID = {"correct", "wrong", "none", "partial"}


def parse_parts() -> list[dict]:
    rows: list[dict] = []
    for path in PARTS:
        cur: tuple[int, str, str] | None = None
        meta: dict[str, str] = {}

        def flush() -> None:
            nonlocal cur, meta
            if cur is None:
                return
            sid, verdict, note = cur
            rows.append(
                {
                    "id": sid,
                    "verdict": verdict.strip().lower(),
                    "note": note.strip(),
                    "cats_line": meta.get("cats", ""),
                    "method_line": meta.get("method", ""),
                    "text": meta.get("text", ""),
                    "url": meta.get("url", ""),
                    "part": path.name,
                }
            )
            cur = None
            meta = {}

        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^(\d+):([^:#]+):(.*)$", line.strip())
            if m:
                flush()
                cur = (int(m.group(1)), m.group(2), m.group(3))
                meta = {}
                continue
            if cur is None:
                continue
            if line.startswith("# cats:"):
                meta["cats"] = line[7:].strip()
            elif line.startswith("# method:"):
                meta["method"] = line[9:].strip()
            elif line.startswith("# text:"):
                meta["text"] = line[7:].strip()
            elif line.startswith("# url:"):
                meta["url"] = line[6:].strip()
        flush()
    return rows


def method_of(s: dict) -> str:
    cls = (s.get("metadata") or {}).get("classification") or {}
    return cls.get("method") or "none"


def source_from_url(url: str) -> str:
    u = (url or "").lower()
    if "tiktok" in u:
        return "tiktok"
    if "reddit" in u:
        return "reddit"
    if "twitter" in u or "x.com" in u:
        return "twitter"
    if u:
        return "news"
    return "?"


def snippet(s: dict, n: int = 200) -> str:
    title = (s.get("title") or "").replace("\n", " ").strip()
    body = (s.get("body") or "").replace("\n", " ").strip()
    if title and body and body != title and len(body) > 20:
        text = f"{title} — {body}"
    else:
        text = title or body or ""
    text = " ".join(text.split())
    return text[:n] + ("…" if len(text) > n else "")


def propose_cluster(r: dict) -> str:
    """Heuristic bucket from human note + method — for human review only."""
    note = (r.get("note") or "").lower()
    method = r.get("method") or ""
    cats = r.get("categories") or []
    verdict = r.get("verdict")

    if method == "inherited" and verdict in {"none", "partial", "wrong"}:
        if any(k in note for k in ("traffic", "video", "news", "inherited")):
            return "inherited_parent_ok_comment_weak"
        return "inherited_non_civic_comment"

    if any(k in note for k in ("waste", "wasted", "mortgage", "rent", "housing", "keyword")):
        if "dorm" in note or "uci" in note:
            return "broad_keyword_non_civic_context"
        if any(k in note for k in ("waste", "wasted", "mortgage")):
            return "broad_keyword_false_positive"
        if "housing" in note or "rent" in note:
            return "broad_keyword_non_civic_context"

    if method == "legacy" or "legacy" in note:
        return "legacy_stale_label"

    if method == "model" and verdict in {"wrong", "partial", "none"}:
        return "model_only_false_positive"

    if verdict == "partial" and any(
        k in note for k in ("drop", "keep", "should", "missing", "also", "video")
    ):
        return "partial_mixed_or_missing_cats"

    if verdict == "none":
        return "non_civic_should_be_uncategorized"

    if verdict == "wrong":
        if cats and "should be []" in note or "no civic" in note or "not " in note:
            return "wrong_category_assignment"
        return "wrong_category_assignment"

    return "other_review"


def build_clusters(fail: list[dict]) -> list[tuple[str, list[dict]]]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in fail:
        buckets[propose_cluster(r)].append(r)
    # order by size
    return sorted(buckets.items(), key=lambda kv: -len(kv[1]))


CLUSTER_TITLES = {
    "inherited_non_civic_comment": (
        "Inherited categories on non-civic TikTok comments",
        "Comment text has no civic issue, but cats came from parent video (`method=inherited`).",
    ),
    "inherited_parent_ok_comment_weak": (
        "Inherited from parent — video OK, comment weak / partial",
        "Humans often say the video is civic but the comment is chatter; inherited cats still apply to the comment row.",
    ),
    "broad_keyword_false_positive": (
        "Broad keyword false positives",
        "Keyword hit on colloquial / incidental words (e.g. waste/wasted, mortgage).",
    ),
    "broad_keyword_non_civic_context": (
        "Keyword match in non-civic context",
        "Real keyword string, but topic is not a city civic issue (e.g. dorm housing).",
    ),
    "legacy_stale_label": (
        "Legacy method stale labels",
        "`method=legacy` assignments that do not match article content.",
    ),
    "model_only_false_positive": (
        "Model-only wrong rescues",
        "`method=model` assigned a category that humans reject.",
    ),
    "partial_mixed_or_missing_cats": (
        "Partial — mixed / missing categories",
        "Some assigned cats OK; others should drop or a needed cat is missing.",
    ),
    "non_civic_should_be_uncategorized": (
        "Non-civic content that should be uncategorized",
        "Lifestyle / fluff / chatter; humans marked `none`.",
    ),
    "wrong_category_assignment": (
        "Wrong category assignment",
        "Has civic-ish or other content, but assigned cat(s) do not fit.",
    ),
    "other_review": (
        "Other / needs human bucket",
        "Did not auto-fit a cluster — please re-bucket by hand.",
    ),
}


def main() -> None:
    human = parse_parts()
    bad = [r for r in human if r["verdict"] not in VALID]
    if bad:
        raise SystemExit(f"Nonstandard verdicts: {bad[:5]}")

    try:
        with urllib.request.urlopen(API, timeout=30) as resp:
            live = {
                int(s["id"]): s for s in json.loads(resp.read().decode("utf-8"))["signals"]
            }
    except Exception as exc:  # noqa: BLE001
        print(f"Live API unavailable ({exc}); using worksheet fields only.")
        live = {}

    signals: list[dict] = []
    missing_live: list[int] = []
    for h in human:
        s = live.get(h["id"])
        if not s:
            missing_live.append(h["id"])
            cats = [
                c.strip()
                for c in h["cats_line"].split(",")
                if c.strip() and c.strip() != "[]"
            ]
            signals.append(
                {
                    "id": h["id"],
                    "source": source_from_url(h["url"]),
                    "method": h["method_line"] or "none",
                    "categories": cats,
                    "snippet": h["text"],
                    "title": h["text"],
                    "body": "",
                    "url": h["url"],
                    "verdict": h["verdict"],
                    "note": h["note"],
                    "part": h["part"],
                }
            )
            continue
        signals.append(
            {
                "id": h["id"],
                "source": s.get("source") or source_from_url(s.get("url") or h["url"]),
                "method": method_of(s),
                "categories": list(s.get("categories") or []),
                "snippet": snippet(s) or h["text"],
                "title": s.get("title") or "",
                "body": (s.get("body") or "")[:500],
                "url": s.get("url") or h["url"],
                "verdict": h["verdict"],
                "note": h["note"],
                "part": h["part"],
            }
        )

    signals.sort(key=lambda r: (r["source"], r["id"]))
    counts = Counter(r["verdict"] for r in signals)
    total = len(signals)

    def pct(v: str) -> str:
        return f"{(counts[v] / total * 100):.0f}%" if total else ""

    by_m: dict[str, Counter] = defaultdict(Counter)
    by_s: dict[str, Counter] = defaultdict(Counter)
    m_tot: Counter = Counter()
    s_tot: Counter = Counter()
    for r in signals:
        by_m[r["method"]][r["verdict"]] += 1
        by_s[r["source"]][r["verdict"]] += 1
        m_tot[r["method"]] += 1
        s_tot[r["source"]] += 1

    fail = [r for r in signals if r["verdict"] in {"wrong", "none", "partial"}]
    clusters = build_clusters(fail)

    # combined answers
    comb: list[str] = [
        "# HUMAN gold answers — merged from part_a + part_b (Session 4)",
        "# Format: id:verdict:comment",
        f"# Rows: {len(signals)}",
        "#",
    ]
    by_id = {r["id"]: r for r in signals}
    for h in sorted(human, key=lambda r: r["id"]):
        srow = by_id[h["id"]]
        cats = ", ".join(srow["categories"]) if srow["categories"] else "[]"
        comb.extend(
            [
                f"{h['id']}:{h['verdict']}:{h['note']}",
                f"# cats: {cats}",
                f"# method: {srow['method']}",
                f"# text: {srow['snippet']}",
                f"# url: {srow['url']}",
                "",
            ]
        )
    COMBINED.write_text("\n".join(comb).rstrip() + "\n", encoding="utf-8")

    payload = {
        "version": 2,
        "date": "2026-08-03",
        "status": "human_gold",
        "reviewers": "Jack + coworker",
        "source_parts": [
            "batch_01_answers_part_a.txt",
            "batch_01_answers_part_b.txt",
        ],
        "note": "Human hand labels. review_batch_01.md remains AI draft only.",
        "storage": "db" if live else "worksheet",
        "db_count_at_promote": len(live),
        "signals": signals,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    lines: list[str] = [
        "# Phase A — Hand Gold Sample (Batch #02)",
        "",
        "**Date:** 2026-08-03 (promoted from part A/B)",
        "**Branch:** `feature/phase-a-gold-hand-s4`",
        "**Reviewers:** Jack + coworker (human)",
        f"**Signals:** {total} hand-labeled",
        "**Status:** human gold — reusable for Session 5 re-score",
        "",
        "> `review_batch_01.md` is AI draft only. This file is the gold sample.",
        ">",
        "> Source worksheets: `batch_01_answers_part_a.txt`, `batch_01_answers_part_b.txt`",
        "",
        "## Verdict key",
        "",
        "- **correct** — assigned categories fit",
        "- **wrong** — categories do not match content",
        "- **none** — no civic issue / should not be categorized",
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

    lines += [
        "",
        "## Top failure modes (human)",
        "",
        "_Draft clusters in [`failure_clusters_draft.md`](failure_clusters_draft.md) — "
        "approve/edit before treating as Session 5 baseline._",
        "",
    ]
    for key, members in clusters[:8]:
        title, blurb = CLUSTER_TITLES.get(key, (key, ""))
        lines.append(f"- **{title}** ({len(members)}) — {blurb}")
    lines += [
        "",
        "---",
        "",
        "## Raw hand review",
        "",
        "Format: `id | source | method | assigned_categories | verdict | notes`",
        "",
    ]

    for src, group_iter in groupby(signals, key=lambda r: r["source"]):
        group = list(group_iter)
        lines.append(f"### {src} ({len(group)})")
        lines.append("")
        for r in group:
            cats = ", ".join(r["categories"]) if r["categories"] else "[]"
            url = r.get("url") or ""
            lines.append(f"**id={r['id']}** · method=`{r['method']}` · cats=`{cats}`")
            if url:
                lines.append(f"- source: <{url}>")
            lines.append(f"> {r['snippet']}")
            lines.append(
                f"`{r['id']} | {r['source']} | {r['method']} | {cats} | {r['verdict']} | {r['note']}`"
            )
            lines.append("")
        lines.append("")

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # draft clusters doc for human review
    cl: list[str] = [
        "# Failure-mode clusters — DRAFT (human approve)",
        "",
        "**Date:** 2026-08-03",
        f"**From:** {total} human gold rows · {len(fail)} wrong/none/partial",
        "**Status:** agent-proposed from notes — **not final** until Jack + coworker edit",
        "",
        "## How to use",
        "",
        "1. Skim each cluster’s member ids + notes.",
        "2. Move mis-bucketed ids; rename/merge clusters if needed.",
        "3. When happy, copy the approved list into `review_batch_02_hand.md` "
        "Top failure modes (replace the draft pointer).",
        "",
        "## Tally snapshot",
        "",
        f"- correct {counts['correct']} ({pct('correct')})",
        f"- partial {counts['partial']} ({pct('partial')})",
        f"- none {counts['none']} ({pct('none')})",
        f"- wrong {counts['wrong']} ({pct('wrong')})",
        "",
    ]
    for key, members in clusters:
        title, blurb = CLUSTER_TITLES.get(key, (key, ""))
        cl += [
            f"## {title} ({len(members)})",
            "",
            blurb,
            "",
            "| id | source | method | cats | verdict | note |",
            "|----|--------|--------|------|---------|------|",
        ]
        for r in sorted(members, key=lambda x: x["id"]):
            cats = ", ".join(r["categories"]) if r["categories"] else "`[]`"
            note = (r["note"] or "").replace("|", "/")
            # Avoid raw * or _ in notes breaking MD emphasis across sections
            note = note.replace("*", "").replace("_", "-")
            cl.append(
                f"| {r['id']} | {r['source']} | {r['method']} | {cats} | {r['verdict']} | {note} |"
            )
        cl.append("")

    CLUSTERS.write_text("\n".join(cl) + "\n", encoding="utf-8")

    print(f"gold rows={total} missing_live={missing_live}")
    print(f"Wrote {OUT_MD.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    print(f"Wrote {COMBINED.relative_to(ROOT)}")
    print(f"Wrote {CLUSTERS.relative_to(ROOT)}")
    print("counts", dict(counts))
    for key, members in clusters:
        print(f"  cluster {key}: {len(members)}")


if __name__ == "__main__":
    main()
