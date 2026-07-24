"""Tests for lenient Reddit / Twitter import paste parsing."""

from __future__ import annotations

import pytest

from scrapers.json_payload import ImportPayloadError, parse_import_payload
from scrapers.reddit.export import scrape_payload_to_signals


def test_parse_strict_json_object():
    payload = parse_import_payload('{"query": "irvine", "items": []}')
    assert payload["query"] == "irvine"
    assert payload["items"] == []


def test_parse_missing_outer_braces():
    payload = parse_import_payload('"query": "irvine", "items": []')
    assert payload["query"] == "irvine"


def test_parse_leading_icon_and_size_marker_near_json():
    # Icon + size marker in front of otherwise-valid JSON object body.
    raw = '▾{"blocked": false, "query": "irvine", "items": []}'
    payload = parse_import_payload(raw)
    assert payload["blocked"] is False
    assert payload["query"] == "irvine"


def test_parse_devtools_tree_dump_reddit_shape():
    dump = """
    ▾{6}
    blocked: false
    listingType: "search"
    query: "irvine"
    subredditFilter: "irvine"
    items: [2]
    ▾0: {5}
    id: "1v3njdq"
    title: "Smoking on Property"
    author: "StonedBooty"
    permalink: "https://old.reddit.com/r/irvine/comments/1v3njdq/smoking/"
    previewText: "Hello. I live in Irvine company housing near Spectrum."
    ▾1: {5}
    id: "1v38c3z"
    title: "5 Frwy N. between Lake Forest and Irvine"
    author: "Ok_Cele2025"
    permalink: "https://old.reddit.com/r/irvine/comments/1v38c3z/5_frwy/"
    previewText: "Around 11:30 PM I saw a lot of firetrucks"
    itemCount: 2
    """
    payload = parse_import_payload(dump)
    assert payload["blocked"] is False
    assert payload["query"] == "irvine"
    assert payload["subredditFilter"] == "irvine"
    assert len(payload["items"]) == 2
    assert payload["items"][0]["id"] == "1v3njdq"
    assert payload["items"][1]["title"].startswith("5 Frwy")
    assert payload["itemCount"] == 2

    signals = scrape_payload_to_signals(payload, civic_only=False)
    assert len(signals) == 2
    assert signals[0].source == "reddit"
    assert "Smoking on Property" in signals[0].title


def test_parse_devtools_glued_no_newlines():
    dump = (
        '▾{4}blocked: falselistingType: "search"query: "irvine"items: [1]'
        '▾0: {3}id: "abc"title: "Pothole on Culver"previewText: "Still there"'
    )
    payload = parse_import_payload(dump)
    assert payload["blocked"] is False
    assert payload["listingType"] == "search"
    assert payload["items"][0]["id"] == "abc"
    assert payload["items"][0]["title"] == "Pothole on Culver"


def test_parse_devtools_nested_twitter_author():
    dump = """
    {3}
    query: "irvine"
    listingType: "twitter-search"
    tweets: [1]
    0: {4}
    id: "123"
    text: "Traffic alert on Culver"
    createdAt: "Tue Jul 07 21:51:23 +0000 2026"
    author: {2}
    name: "Irvine Police"
    handle: "IrvinePolice"
    """
    payload = parse_import_payload(dump)
    assert payload["tweets"][0]["author"]["handle"] == "IrvinePolice"
    assert payload["tweets"][0]["text"].startswith("Traffic alert")


def test_parse_devtools_preview_text_with_inner_quotes():
    """Reddit previewText often has raw quotes; `{N}` counts then look 'short'."""
    dump = """
    {4}
    query: "irvine"
    subredditFilter: "irvine"
    items: [1]
    0: {22}
    id: "1v1el6b"
    rank: null
    subreddit: "irvine"
    subredditPrefixed: "r/irvine"
    author: "komplete"
    title: "IVC Public Access Channel"
    permalink: "https://old.reddit.com/r/irvine/comments/1v1el6b/ivc/"
    shortlink: "https://redd.it/1v1el6b"
    url: "https://old.reddit.com/r/irvine/comments/1v1el6b/ivc/"
    domain: null
    createdAt: "2026-07-20T07:29:59+00:00"
    flair: null
    score: 10
    scoreText: "10 points"
    commentCount: 2
    commentCountText: "2 comments"
    previewText: "My wife and I called it the "Circles and Music channel" because it played music."
    thumbnailUrl: null
    nsfw: false
    spoiler: false
    locked: false
    stickied: false
    itemCount: 1
    """
    payload = parse_import_payload(dump)
    assert len(payload["items"]) == 1
    item = payload["items"][0]
    assert item["id"] == "1v1el6b"
    assert "Circles and Music channel" in item["previewText"]
    assert item["stickied"] is False
    assert payload["itemCount"] == 1

def test_parse_devtools_short_object_count_still_keeps_items():
    # Marker says 5 props but only 3 are present — must not hard-fail.
    dump = '{5}query: "irvine"items: [0]itemCount: 0'
    payload = parse_import_payload(dump)
    assert payload["query"] == "irvine"
    assert payload["items"] == []


def test_parse_rejects_array_root():
    with pytest.raises(ImportPayloadError):
        parse_import_payload("[1, 2, 3]")
