from dataclasses import dataclass, field

from scrapers.categories import CivicIssueCategory, DEFAULT_SEARCH_TERMS


@dataclass
class TikTokScrapeConfig:
    """Geographic and query settings for TikTok civic-issue comment scraping."""

    city: str
    state: str = "CA"
    neighborhood: str | None = None
    categories: list[CivicIssueCategory] = field(
        default_factory=lambda: list(CivicIssueCategory)
    )
    max_videos_per_query: int = 5
    max_comments_per_video: int = 50
    headless: bool = False

    def location_label(self) -> str:
        if self.neighborhood:
            return f"{self.neighborhood}, {self.city}, {self.state}"
        return f"{self.city}, {self.state}"

    def search_queries(self) -> list[str]:
        """Build TikTok search strings combining civic terms with the target area."""
        area = self.location_label()
        queries: list[str] = []
        for category in self.categories:
            for term in DEFAULT_SEARCH_TERMS[category]:
                queries.append(f"{term} {area}")
        return queries
