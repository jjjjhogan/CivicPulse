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


def test_short_inherited_comment_cleared():
    rows = _load("tiktok.json")
    short = next(
        r for r in rows
        if r["metadata"].get("inherited_from_video") and r["body"] == "lol same"
    )
    reclassify_row(short)
    assert short["categories"] == []
    cls = short["metadata"]["classification"]
    assert cls["method"] == "none"


def test_long_inherited_comment_keeps_categories():
    rows = _load("tiktok.json")
    long_comment = next(
        r for r in rows
        if r["metadata"].get("inherited_from_video")
        and "intersection" in r["body"]
    )
    reclassify_row(long_comment)
    assert long_comment["categories"]
    cls = long_comment["metadata"]["classification"]
    assert cls["method"] in {"inherited", "keywords", "keywords+model", "model"}
    assert 0 <= cls["confidence"] <= 1


def test_thread_consensus_for_tiktok():
    rows = _load("tiktok.json")
    consensus = thread_consensus(rows)
    assert isinstance(consensus, dict)
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


def test_old_categories_cleared_when_classifier_returns_nothing():
    row = {
        "source": "news",
        "title": "Summer concert series at the amphitheater",
        "body": "Live music every Friday with food trucks and lawn games",
        "url": "https://example.com/concerts",
        "categories": ["housing"],
        "metadata": {"classification": {"method": "legacy", "confidence": 0.6}},
    }
    reclassify_row(row)
    assert row["categories"] == []
    assert row["metadata"]["classification"]["method"] == "none"
