"""Shared civic issue categories used across ingestion sources."""

from enum import Enum
import re

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "potholes": [
        "pothole",
        "road damage",
        "pavement crack",
        "street repair",
        "road repair",
        "street resurfacing",
        "slurry seal",
    ],
    "noise": [
        "noise complaint",
        "loud music",
        "construction noise",
        "loud neighbors",
        "noise ordinance",
        "helicopter noise",
    ],
    "sanitation": [
        "trash pickup",
        "garbage",
        "illegal dumping",
        "sanitation",
        "recycling",
        "waste",
        "litter",
    ],
    "public_safety": [
        "break-in",
        "shooting",
        "assault",
        "streetlight out",
        "crime",
        "police",
        "flood",
        "flooding",
        "flash flood",
        "evacuate",
        "evacuation",
        "wildfire",
        "brush fire",
        "car chase",
        "pursuit",
        "traffic collision",
        "crash",
        "accident",
        "protest",
        "demonstration",
        "standoff",
        "hostage",
        "missing person",
        "emergency",
        "first responder",
        "fire department",
        "swatting",
    ],
    "housing": [
        "eviction",
        "rent increase",
        "affordable housing",
        "homeless",
        "housing crisis",
        "rent",
        "zoning",
        "housing",
        "apartment",
        "tenant",
    ],
    "immigration": [
        "immigration",
        "immigrant",
        "deportation",
        "ice raid",
        "ice protest",
        "ice agents",
        "border patrol",
        "detention center",
        "migrant",
        "asylum",
    ],
}


class CivicIssueCategory(str, Enum):
    POTHOLES = "potholes"
    NOISE = "noise"
    SANITATION = "sanitation"
    PUBLIC_SAFETY = "public_safety"
    HOUSING = "housing"
    IMMIGRATION = "immigration"


DEFAULT_SEARCH_TERMS: dict[CivicIssueCategory, list[str]] = {
    CivicIssueCategory.POTHOLES: CATEGORY_KEYWORDS["potholes"],
    CivicIssueCategory.NOISE: CATEGORY_KEYWORDS["noise"],
    CivicIssueCategory.SANITATION: CATEGORY_KEYWORDS["sanitation"],
    CivicIssueCategory.PUBLIC_SAFETY: CATEGORY_KEYWORDS["public_safety"],
    CivicIssueCategory.HOUSING: CATEGORY_KEYWORDS["housing"],
    CivicIssueCategory.IMMIGRATION: CATEGORY_KEYWORDS["immigration"],
}


def _matches(keyword: str, text: str) -> bool:
    # Word-boundary start so short tokens like "rent" match "rents" but not "current".
    return re.search(r"\b" + re.escape(keyword), text) is not None


def classify(text: str) -> list[str]:
    text_lower = (text or "").lower()
    if not text_lower.strip():
        return []
    return [
        category
        for category, keywords in CATEGORY_KEYWORDS.items()
        if any(_matches(keyword, text_lower) for keyword in keywords)
    ]
