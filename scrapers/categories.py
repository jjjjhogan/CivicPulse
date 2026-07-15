"""Shared civic issue categories used across ingestion sources."""

from __future__ import annotations

import re
from enum import Enum

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "potholes": [
        "pothole",
        "road damage",
        "pavement crack",
        "pavement",
        "street repair",
        "road repair",
        "street resurfacing",
        "slurry seal",
        "roadwork",
        "road work",
        "sinkhole",
        "cracked road",
        "bumpy road",
        "asphalt",
        "road closure",
    ],
    "noise": [
        "noise complaint",
        "noise",
        "noisy",
        "loud music",
        "loud party",
        "loud parties",
        "construction noise",
        "loud neighbors",
        "noise ordinance",
        "helicopter noise",
        "barking",
        "fireworks",
        "leaf blower",
    ],
    "sanitation": [
        "trash pickup",
        "trash",
        "garbage",
        "litter",
        "illegal dumping",
        "sanitation",
        "recycling",
        "waste",
        "dumpster",
        "sewage",
        "sewer",
        "landfill",
        "rats",
        "rodent",
        "graffiti",
    ],
    "public_safety": [
        "break-in",
        "burglary",
        "robbery",
        "theft",
        "stolen",
        "shooting",
        "gunshot",
        "assault",
        "streetlight out",
        "street light",
        "crime",
        "police",
        "cops",
        "sheriff",
        "arrest",
        "vandalism",
        "unsafe",
        "dangerous",
        "sketchy",
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
        "hazmat",
        "fbi",
        "hit and run",
        "speeding",
        "reckless driving",
        "car break",
    ],
    "housing": [
        "eviction",
        "evicted",
        "rent increase",
        "rent hike",
        "affordable housing",
        "homeless",
        "unhoused",
        "housing crisis",
        "rent",
        "zoning",
        "housing",
        "landlord",
        "lease",
        "mortgage",
        "apartment",
        "tenant",
        "overpriced",
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


# City-mode search runs one TikTok query per term, so keep this list short and
# high-signal instead of reusing the full classification keyword lists above.
DEFAULT_SEARCH_TERMS: dict[CivicIssueCategory, list[str]] = {
    CivicIssueCategory.POTHOLES: ["pothole", "road damage", "street repair"],
    CivicIssueCategory.NOISE: ["noise complaint", "construction noise", "loud neighbors"],
    CivicIssueCategory.SANITATION: ["trash pickup", "garbage", "illegal dumping"],
    CivicIssueCategory.PUBLIC_SAFETY: ["crime", "police", "streetlight out"],
    CivicIssueCategory.HOUSING: ["rent increase", "affordable housing", "homeless"],
    CivicIssueCategory.IMMIGRATION: ["immigration", "ice protest", "deportation"],
}

_CATEGORY_PATTERNS: dict[str, re.Pattern[str]] = {
    # Word-prefix matching: "rent" hits "rent"/"rents"/"rental" but not
    # "parent"; "crime" hits "crimes"; "rats" doesn't hit "congrats".
    category: re.compile(r"\b(?:" + "|".join(re.escape(k) for k in keywords) + r")")
    for category, keywords in CATEGORY_KEYWORDS.items()
}


def classify(text: str) -> list[str]:
    text_lower = (text or "").lower()
    if not text_lower.strip():
        return []
    return [
        category
        for category, pattern in _CATEGORY_PATTERNS.items()
        if pattern.search(text_lower)
    ]
