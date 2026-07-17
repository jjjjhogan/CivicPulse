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
    # Hand-labeled paraphrase without the literal keyword "pothole".
    result = classify_signal(
        "Hit a huge dip on Irvine Blvd and my rim is bent"
    )
    assert "potholes" in result.categories
    assert result.method in {"model", "keywords+model", "keywords"}
    assert result.confidence > 0
