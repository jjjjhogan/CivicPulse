"""Shared output schema for CivicPulse ingestion sources."""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class CivicSignal:
    """
    Normalized resident signal from any ingestion source.

    `to_landing_page_dict()` matches the shape used by index.html / script.js on main.
    """

    source: str
    outlet: str
    title: str
    body: str = ""
    url: str = ""
    categories: list[str] = field(default_factory=list)
    published_utc: str = ""
    metadata: dict = field(default_factory=dict)

    def to_landing_page_dict(self) -> dict:
        return {
            "outlet": self.outlet,
            "title": self.title,
            "categories": self.categories,
            "published_utc": self.published_utc,
        }

    def to_dict(self) -> dict:
        return asdict(self)


def timestamp_to_date(epoch_seconds: float) -> str:
    return datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime("%Y-%m-%d")
