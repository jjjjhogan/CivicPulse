"""Shared civic issue categories used across ingestion sources."""

import re
from enum import Enum

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "potholes": [
        "pothole",
        "road damage",
        "pavement",
        "street repair",
        "road repair",
        "roadwork",
        "road work",
        "sinkhole",
        "cracked road",
        "bumpy road",
        "asphalt",
        "road closure",
    ],
    "noise": [
        "noise",
        "noisy",
        "loud music",
        "loud party",
        "loud parties",
        "construction noise",
        "loud neighbors",
        "barking",
        "fireworks",
        "leaf blower",
    ],
    "sanitation": [
        "trash",
        "garbage",
        "litter",
        "illegal dumping",
        "sanitation",
        "dumpster",
        "sewage",
        "sewer",
        "landfill",
        "recycling",
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
        "emergency",
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
        "rent",
        "rent increase",
        "rent hike",
        "affordable housing",
        "homeless",
        "unhoused",
        "housing",
        "landlord",
        "lease",
        "mortgage",
        "tenant",
        "apartment",
        "overpriced",
    ],
}


class CivicIssueCategory(str, Enum):
    POTHOLES = "potholes"
    NOISE = "noise"
    SANITATION = "sanitation"
    PUBLIC_SAFETY = "public_safety"
    HOUSING = "housing"


# City-mode search runs one TikTok query per term, so keep this list short and
# high-signal instead of reusing the full classification keyword lists above.
DEFAULT_SEARCH_TERMS: dict[CivicIssueCategory, list[str]] = {
    CivicIssueCategory.POTHOLES: ["pothole", "road damage", "street repair"],
    CivicIssueCategory.NOISE: ["noise complaint", "construction noise", "loud neighbors"],
    CivicIssueCategory.SANITATION: ["trash pickup", "garbage", "illegal dumping"],
    CivicIssueCategory.PUBLIC_SAFETY: ["crime", "police", "streetlight out"],
    CivicIssueCategory.HOUSING: ["rent increase", "affordable housing", "homeless"],
}

_CATEGORY_PATTERNS: dict[str, re.Pattern] = {
    # Word-prefix matching: "rent" hits "rent"/"rents"/"rental" but not
    # "parent"; "crime" hits "crimes"; "rats" doesn't hit "congrats".
    category: re.compile(r"\b(?:" + "|".join(re.escape(k) for k in keywords) + r")")
    for category, keywords in CATEGORY_KEYWORDS.items()
}


def classify(text: str) -> list[str]:
    text_lower = text.lower()
    return [
        category
        for category, pattern in _CATEGORY_PATTERNS.items()
        if pattern.search(text_lower)
    ]
