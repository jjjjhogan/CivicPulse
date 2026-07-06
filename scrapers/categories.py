"""Shared civic issue categories used across ingestion sources."""

from enum import Enum

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "potholes": ["pothole", "road damage", "pavement crack", "street repair"],
    "noise": ["noise complaint", "loud music", "construction noise", "loud neighbors"],
    "sanitation": ["trash pickup", "garbage", "illegal dumping", "sanitation"],
    "public_safety": ["break-in", "shooting", "assault", "streetlight out", "crime", "police"],
    "housing": ["eviction", "rent increase", "affordable housing", "homeless", "housing crisis"],
}


class CivicIssueCategory(str, Enum):
    POTHOLES = "potholes"
    NOISE = "noise"
    SANITATION = "sanitation"
    PUBLIC_SAFETY = "public_safety"
    HOUSING = "housing"


DEFAULT_SEARCH_TERMS: dict[CivicIssueCategory, list[str]] = {
    CivicIssueCategory.POTHOLES: CATEGORY_KEYWORDS["potholes"],
    CivicIssueCategory.NOISE: CATEGORY_KEYWORDS["noise"],
    CivicIssueCategory.SANITATION: CATEGORY_KEYWORDS["sanitation"],
    CivicIssueCategory.PUBLIC_SAFETY: CATEGORY_KEYWORDS["public_safety"],
    CivicIssueCategory.HOUSING: CATEGORY_KEYWORDS["housing"],
}


def classify(text: str) -> list[str]:
    text_lower = text.lower()
    return [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(keyword in text_lower for keyword in keywords)
    ]
