import requests
from urllib.parse import urljoin
from src.config import URLS
from src.models import NewsArticle
import xml.etree.ElementTree as ET


def fetch_news(category: str):
    url = URLS[category]

    response = requests.get(
        url,
        timeout=10,
        headers={
             "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        },
    )

    response.raise_for_status()

    return ET.fromstring(response.content)

def extract_links(root, category: str):
    news_items = []

    items = root.findall(".//item")

    print("TOTAL ITEMS:",len(items))

    for rank, item in enumerate(items[:10], start=1):
        title = item.findtext("title")
        url = item.findtext("link")
        published_at = item.findtext("pubDate")

        source_tag = item.find("source")
        source = source_tag.text if source_tag is not None else None

        news_items.append(
            {
                "category": category,
                "rank": rank,
                "title": title,
                "description": None,
                "source": source,
                "published_at": published_at,
                "url": url,
            }
        )

    return news_items