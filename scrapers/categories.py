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
        "waste collection",
        "waste management",
        "waste bin",
        "dumpster",
        "sewage",
        "sewer",
        "landfill",
        "rats",
        "rodent",
        "graffiti",
    ],
    # The old catch-all "public_safety" list is split into specific
    # categories — murder and package theft are different civic issues.
    # "public_safety" remains as the residual bucket for general policing,
    # protests, and unease that don't fit a specific crime type.
    "violent_crime": [
        "shooting",
        "shots fired",
        "gunfire",
        "gunshot",
        "stabbing",
        "stabbed",
        "murder",
        "homicide",
        "manslaughter",
        "assault",
        "robbery",
        "mugging",
        "mugged",
        "carjacking",
        "kidnapping",
        "kidnapped",
        "active shooter",
        "domestic violence",
        "standoff",
        "hostage",
        "swatting",
    ],
    "property_crime": [
        "break-in",
        "broke into",
        "broken into",
        "burglary",
        "burglar",
        "theft",
        "thief",
        "thieves",
        "stolen",
        "shoplifting",
        "shoplifter",
        "vandalism",
        "vandalized",
        "porch pirate",
        "catalytic converter",
        "car break",
        "looting",
        "looted",
    ],
    "traffic_safety": [
        "traffic collision",
        "crash",
        "car accident",
        "traffic accident",
        "vehicle accident",
        "fatal accident",
        "accident scene",
        "hit and run",
        "speeding",
        "reckless driving",
        "street racing",
        "street racer",
        "car chase",
        "pursuit",
        "crosswalk",
        "red light",
        "stop sign",
        "school zone",
        "drunk driver",
        "drunk driving",
        "road rage",
        "jaywalk",
    ],
    "emergencies": [
        "flood",
        "flooding",
        "flash flood",
        "evacuate",
        "evacuation",
        "wildfire",
        "brush fire",
        "house fire",
        "structure fire",
        "hazmat",
        "gas leak",
        "power line",
        "power outage",
        "earthquake",
        "mudslide",
        "landslide",
        "emergency",
        "first responder",
        "fire department",
        "firefighter",
    ],
    "public_safety": [
        "crime",
        "police",
        "cops",
        "sheriff",
        "arrest",
        "unsafe",
        "dangerous",
        "sketchy",
        "suspicious",
        "stalker",
        "stalking",
        "harass",
        "protest",
        "demonstration",
        "missing person",
        "streetlight out",
        "street light",
        "fbi",
    ],
    # Hard phrases always assign housing. Bare rent/housing/homeless live in
    # HOUSING_SOFT_KEYWORDS and only count when the classifier's soft+veto
    # path agrees (model does not prefer "none", and ad blocklist misses).
    "housing": [
        "eviction",
        "evicted",
        "rent increase",
        "rent hike",
        "rent price",
        "rent prices",
        "rent control",
        "rent burden",
        "average rent",
        "raised the rent",
        "raising rent",
        "affordable housing",
        "housing crisis",
        "housing cost",
        "housing shortage",
        "housing prices",
        "section 8",
        "below-market",
        "sleeping in cars",
        "homeless encampment",
        "homelessness crisis",
        "homeless services",
        "homeless shelter",
        "unhoused residents",
        "unhoused population",
        "mold and roaches",
        "zoning",
        "landlord",
        "tenant",
        "utility price hike",
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

# Soft housing tokens — propose only; scrapers/classifier.py may veto.
HOUSING_SOFT_KEYWORDS: list[str] = [
    "rent",
    "housing",
    "homeless",
    "unhoused",
]

# Listing / amenity / dorm speak that should never become housing via soft hits.
HOUSING_AD_BLOCKLIST: list[str] = [
    "for rent",
    "for lease",
    "now leasing",
    "now available",
    "available for lease",
    "list price",
    "sq ft",
    "sqft",
    "amenities",
    "pool and gym",
    "floor plan",
    "themed housing",
    "roommate",
    "roommates",
    "moving company",
    "3 bed",
    "2 bath",
    "3 bath",
    "br/ba",
]


class CivicIssueCategory(str, Enum):
    POTHOLES = "potholes"
    NOISE = "noise"
    SANITATION = "sanitation"
    VIOLENT_CRIME = "violent_crime"
    PROPERTY_CRIME = "property_crime"
    TRAFFIC_SAFETY = "traffic_safety"
    EMERGENCIES = "emergencies"
    PUBLIC_SAFETY = "public_safety"
    HOUSING = "housing"
    IMMIGRATION = "immigration"


# City-mode search runs one TikTok query per term, so keep this list short and
# high-signal instead of reusing the full classification keyword lists above.
DEFAULT_SEARCH_TERMS: dict[CivicIssueCategory, list[str]] = {
    CivicIssueCategory.POTHOLES: ["pothole", "road damage", "street repair"],
    CivicIssueCategory.NOISE: ["noise complaint", "construction noise", "loud neighbors"],
    CivicIssueCategory.SANITATION: ["trash pickup", "garbage", "illegal dumping"],
    CivicIssueCategory.VIOLENT_CRIME: ["shooting", "assault", "robbery"],
    CivicIssueCategory.PROPERTY_CRIME: ["theft", "break-in", "catalytic converter"],
    CivicIssueCategory.TRAFFIC_SAFETY: ["car crash", "hit and run", "speeding"],
    CivicIssueCategory.EMERGENCIES: ["wildfire", "flooding", "evacuation"],
    CivicIssueCategory.PUBLIC_SAFETY: ["crime", "police", "streetlight out"],
    CivicIssueCategory.HOUSING: ["rent increase", "affordable housing", "housing prices"],
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
