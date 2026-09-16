from dataclasses import dataclass


@dataclass
class NewsArticle:
    url: str
    title: str
    description: str | None
    source: str
    published_at: str
    rank: str
    category: str