"""Reprocess helpers — classification metadata shape on fixture rows."""

import json
from pathlib import Path

from scrapers.reprocess import reclassify_row, thread_consensus

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "signals"


def _load(name: str) -> list[dict]:
    with open(FIXTURES / name, encoding="utf-8") as handle:
        return json.load(handle)


def test_keyword_row_gets_classification_method():
    row = _load("reddit.json")[0]
    reclassify_row(row)
    cls = row["metadata"]["classification"]
    assert row["categories"]
    assert cls["method"] in {"keywords", "keywords+model", "model"}
    assert isinstance(cls["confidence"], float)
    assert 0 <= cls["confidence"] <= 1
    assert isinstance(cls["scores"], dict)


def test_inherited_tiktok_comment_keeps_categories():
    rows = _load("tiktok.json")
    inherited = next(r for r in rows if r["metadata"].get("inherited_from_video"))
    # Weak comment text alone should not classify; inheritance path applies.
    reclassify_row(inherited)
    assert inherited["categories"] == ["potholes"]
    cls = inherited["metadata"]["classification"]
    assert cls["method"] in {"inherited", "outlet_default", "legacy", "keywords", "keywords+model", "model"}
    assert 0 <= cls["confidence"] <= 1


def test_thread_consensus_for_tiktok():
    rows = _load("tiktok.json")
    consensus = thread_consensus(rows)
    assert isinstance(consensus, dict)
    # Video 1001 has a strong pothole comment in the thread.
    assert "https://www.tiktok.com/@user/video/1001" in consensus
    assert "potholes" in consensus["https://www.tiktok.com/@user/video/1001"]


def test_empty_civic_text_clears_or_marks_none():
    row = {
        "source": "news",
        "title": "Weekend festival draws crowds",
        "body": "Music and food trucks",
        "url": "https://example.com/x",
        "categories": [],
        "metadata": {},
    }
    reclassify_row(row)
    cls = row["metadata"]["classification"]
    assert cls["method"] in {"none", "model", "keywords", "keywords+model"}
    assert isinstance(row["categories"], list)
    assert 0 <= cls["confidence"] <= 1
