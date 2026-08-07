"""Classifier unit tests — stable keyword / model behavior."""

from scrapers.classifier import MODEL_VERSION, classify_signal


def test_pothole_keyword_smoke():
    result = classify_signal("pothole on Culver wrecked my rim")
    assert result.categories == ["potholes"]
    assert result.method == "keywords"
    assert result.confidence == 0.7
    assert result.scores["potholes"] == 0.7


def test_short_nonsense_is_none():
    result = classify_signal("xyz")
    assert result.categories == []
    assert result.method == "none"


def test_empty_text_is_none():
    result = classify_signal("")
    assert result.categories == []
    assert result.method == "none"


def test_multi_keyword_noise():
    result = classify_signal(
        "Neighbors blasting music until 2am with loud construction noise"
    )
    assert "noise" in result.categories
    assert result.method in {"keywords", "keywords+model"}
    assert result.scores
    assert 0 < result.confidence <= 1


def test_to_dict_shape():
    payload = classify_signal("pothole on Culver").to_dict()
    assert payload["method"] in {"keywords", "keywords+model", "model", "none"}
    assert payload["model_version"] == MODEL_VERSION
    assert "scores" in payload
    assert "confidence" in payload


def test_model_paraphrase_from_labels():
    result = classify_signal(
        "Hit a huge dip on Irvine Blvd and my rim is bent"
    )
    assert "potholes" in result.categories
    assert result.method in {"model", "keywords+model", "keywords"}
    assert result.confidence > 0


def test_event_listing_is_none():
    result = classify_signal(
        "Free concert at the amphitheater this weekend, food trucks and lawn games"
    )
    assert result.categories == []
    assert result.method == "none"


def test_housing_ad_is_not_housing_issue():
    result = classify_signal(
        "Three bed two bath condo available for lease near the park, pool and gym"
    )
    assert "housing" not in result.categories


def test_soft_housing_rent_burden_assigns():
    result = classify_signal("My rent is sixty percent of my paycheck now")
    assert "housing" in result.categories


def test_soft_housing_vetoes_lifestyle_rent_complaint():
    result = classify_signal("The rent is the scariest thing in Irvine!")
    assert "housing" not in result.categories


def test_soft_housing_blocklists_themed_housing():
    result = classify_signal(
        "may I ask how you found your roommates? and if you know how themed housing works"
    )
    assert "housing" not in result.categories


def test_hard_housing_phrase_still_assigns():
    result = classify_signal(
        "Average rent prices have risen from 300 to over 2000 a month"
    )
    assert "housing" in result.categories
    assert result.method in {"keywords", "keywords+model"}


def test_multi_category_assignment():
    result = classify_signal(
        "Gas leak forced the block to evacuate, fire trucks and police everywhere"
    )
    assert len(result.categories) >= 1
    assert "emergencies" in result.categories
