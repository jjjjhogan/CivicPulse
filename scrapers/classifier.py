"""
Signal classification with confidence — keywords plus a simple model pass.

Layered on top of the keyword lists in scrapers/categories.py:

1. Keyword pass — the same word-prefix patterns as categories.classify(),
   but counting distinct keyword hits per category so multi-hit matches
   score higher than a single grazing hit.
2. Model pass — a dependency-free multinomial Naive Bayes (one binary
   model per category, unigrams + bigrams, Laplace smoothing) trained on
   the hand-labeled examples in data/labels/labeled_signals.json. Those
   examples are phrased the way residents actually write — mostly without
   the literal keywords — so the model catches paraphrases the keyword
   pass misses ("my rim is bent", "landlord raised the lease renewal").

classify_signal() combines both: keyword hits always assign a category;
the model can add categories on its own only above MODEL_THRESHOLD, which
is what rescues "missed stories" that keywords alone would have dropped.

The result carries per-category scores, an overall confidence, and the
method that produced the labels, embedded in signals as
metadata["classification"] by the export pipelines.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from scrapers.categories import CATEGORY_KEYWORDS, _CATEGORY_PATTERNS

MODEL_VERSION = "nb-v1"
LABELS_PATH = Path(__file__).resolve().parent.parent / "data" / "labels" / "labeled_signals.json"

# Model-only assignments (no keyword support) need a confident softmax
# probability, enough content words to reason about, and at least
# MIN_EVIDENCE distinct words seen in that category's training examples —
# otherwise one stray shared token ("area", "july") can carry an unrelated
# post over the line.
MODEL_THRESHOLD = 0.7
MODEL_SUPPORT = 0.5  # model agreement that boosts an existing keyword match
MIN_MODEL_TOKENS = 3
MIN_EVIDENCE = 2

# The negative examples form their own class, so chatter that merely *looks
# casual* ("lost my cat", "who wants to play pickup") competes against real
# category evidence instead of disappearing into a one-vs-rest average.
NONE_CLASS = "__none__"

# Function words plus local place names. Place names show up in the labeled
# examples as local flavor ("pothole on Jamboree"), and without this list the
# model learns geography as category evidence — every "#irvine" comment
# starts looking like a pothole report.
_STOPWORDS = frozenset(
    """
    a an and are at be been but by can could did do doe for from get got had
    ha have he her hi i if in is it it' its just me my no not of on or our out
    she so than that the their them they thi to us wa we were what when where
    which who will with would you your
    irvine tustin newport beach costa mesa santa ana anaheim orange county
    city california socal oc culver jamboree alton barranca walnut yale
    woodbridge woodbury northwood portola spectrum uci
    """.split()
)

# Confidence attached to categories that were not classified from the text
# itself (TikTok comments inheriting the video's categories, trusted-outlet
# defaults). Kept here so pipelines and reprocessing agree on the numbers.
INHERITED_CONFIDENCE = 0.4
OUTLET_DEFAULT_CONFIDENCE = 0.3


@dataclass
class Classification:
    categories: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    method: str = "none"  # keywords | model | keywords+model | none
    rescued: bool = False  # true when keywords found nothing but the model did

    def to_dict(self) -> dict:
        payload = {
            "scores": self.scores,
            "confidence": self.confidence,
            "method": self.method,
            "model_version": MODEL_VERSION,
        }
        if self.rescued:
            payload["rescued"] = True
        return payload


def _normalize(word: str) -> str:
    # Fold trivial plurals/possessives so "rims" matches training "rim".
    word = word.rstrip("'").removesuffix("'s")
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        word = word[:-1]
    return word


def _content_words(text: str) -> list[str]:
    words = [_normalize(w) for w in re.findall(r"[a-z][a-z']+", (text or "").lower())]
    return [w for w in words if w not in _STOPWORDS]


def _tokenize(text: str) -> list[str]:
    words = _content_words(text)
    return words + [f"{a} {b}" for a, b in zip(words, words[1:])]


def keyword_hits(text: str) -> dict[str, int]:
    """Distinct keyword matches per category (empty dict entries omitted)."""
    text_lower = (text or "").lower()
    if not text_lower.strip():
        return {}
    hits: dict[str, int] = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        if not _CATEGORY_PATTERNS[category].search(text_lower):
            continue
        count = sum(
            1 for kw in keywords if re.search(r"\b" + re.escape(kw), text_lower)
        )
        hits[category] = max(1, count)
    return hits


class _NaiveBayes:
    """Multiclass multinomial Naive Bayes: 6 categories + a "none" class."""

    def __init__(self, examples: list[dict]):
        self.vocab: set[str] = set()
        docs = [(_tokenize(ex["text"]), set(ex.get("categories") or [])) for ex in examples]
        for tokens, _ in docs:
            self.vocab.update(tokens)
        self.classes = list(CATEGORY_KEYWORDS) + [NONE_CLASS]
        self.counts: dict[str, dict[str, int]] = {c: {} for c in self.classes}
        self.totals: dict[str, int] = {c: 0 for c in self.classes}
        for tokens, cats in docs:
            for cls in cats or [NONE_CLASS]:
                self.totals[cls] += len(tokens)
                counts = self.counts[cls]
                for t in tokens:
                    counts[t] = counts.get(t, 0) + 1

    def evidence(self, category: str, words: list[str]) -> set[str]:
        """Distinct words that occur in the category's training examples."""
        counts = self.counts[category]
        return {w for w in words if w in counts}

    def probabilities(self, tokens: list[str]) -> dict[str, float]:
        """Softmax class probabilities from uniform priors (small classes
        shouldn't be penalized for being small)."""
        v = len(self.vocab)
        known = [t for t in tokens if t in self.vocab]
        logs = {
            cls: sum(
                math.log((self.counts[cls].get(t, 0) + 1) / (self.totals[cls] + v))
                for t in known
            )
            for cls in self.classes
        }
        peak = max(logs.values())
        exp = {cls: math.exp(value - peak) for cls, value in logs.items()}
        total = sum(exp.values())
        return {cls: value / total for cls, value in exp.items()}


_model: _NaiveBayes | None = None


def _get_model() -> _NaiveBayes:
    global _model
    if _model is None:
        with open(LABELS_PATH, encoding="utf-8") as handle:
            payload = json.load(handle)
        _model = _NaiveBayes(payload["examples"])
    return _model


def _keyword_score(hits: int) -> float:
    # 1 hit = 0.7, 2 hits = 0.8, 3+ hits = 0.9
    return 0.7 + 0.1 * min(hits - 1, 2)


def classify_signal(text: str) -> Classification:
    tokens = _tokenize(text)
    hits = keyword_hits(text)
    model = _get_model()
    probs = model.probabilities(tokens)
    model_probs = {category: probs[category] for category in CATEGORY_KEYWORDS}

    scores: dict[str, float] = {}
    used_model = False
    for category, count in hits.items():
        score = _keyword_score(count)
        if model_probs[category] >= MODEL_SUPPORT:
            score = min(0.97, score + 0.07)
            used_model = True
        scores[category] = round(score, 3)

    rescued = False
    content = _content_words(text)
    if len(content) >= MIN_MODEL_TOKENS:
        for category, prob in model_probs.items():
            if category in scores or prob < MODEL_THRESHOLD:
                continue
            if len(model.evidence(category, content)) < MIN_EVIDENCE:
                continue
            scores[category] = round(min(prob, 0.9), 3)
            used_model = True
            if not hits:
                rescued = True

    categories = sorted(scores, key=lambda c: -scores[c])
    if not categories:
        method = "none"
        confidence = round(1 - max(model_probs.values(), default=0.0), 3)
    elif hits:
        method = "keywords+model" if used_model else "keywords"
        confidence = round(sum(scores.values()) / len(scores), 3)
    else:
        method = "model"
        confidence = round(sum(scores.values()) / len(scores), 3)

    return Classification(
        categories=categories,
        scores=scores,
        confidence=confidence,
        method=method,
        rescued=rescued,
    )


def inherited_classification(categories: list[str], *, outlet_default: bool = False) -> dict:
    """classification metadata for categories not derived from the text itself."""
    confidence = OUTLET_DEFAULT_CONFIDENCE if outlet_default else INHERITED_CONFIDENCE
    return {
        "scores": {category: confidence for category in categories},
        "confidence": confidence,
        "method": "outlet_default" if outlet_default else "inherited",
        "model_version": MODEL_VERSION,
    }
