import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from src.config import URLS
from src.models import NewsArticle
import xml.etree.ElementTree as ET


def fetch_news(category: str) ->BeautifulSoup:
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

    return BeautifulSoup(response.text, "html.parser")

def extract_links(soup: BeautifulSoup, category: str):
    news_items = []

    links = soup.find_all("a")

    rank= 1

    for link  in links:
        title = link.get_text(" " , strip=True)
        href = link.get("href")

        if not title:
            continue

        if not href:
            continue

        if not href.startswith("./read/"):
            continue

        card = link.parent

        source_tag = card.find("div", class_="vr1PYe")
        time_tag = card.find("time")

        source = source_tag.get_text(strip=True) if source_tag else None
        published_at = time_tag.get("datetime") if time_tag else None   
            
        full_url =urljoin(URLS["base"], href)

        news_items.append(
            {
                "category" : category,
                "title": title,
                "url" : full_url,
                "rank" : rank,
                "published_at" : published_at,
                "source" : source
            }
        )
        rank += 1
    return news_items       