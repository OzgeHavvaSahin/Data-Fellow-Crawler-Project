import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from src.models import NewsArticle

BASE_URL = "https://news.google.com/"

def fetch_news(url: str) ->BeautifulSoup:
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

def extract_links(soup):
    news_items = []

    links = soup.find_all("a")

    for link in links:
        title = link.get_text(" " , strip=True)
        href = link.get("href")

        if not title:
            continue

        if not href:
            continue

        if not href.startswith("./read/"):
            continue

        full_url =urljoin(BASE_URL, href)

        news_items.append(
            {
                "title": title,
                "url" : full_url,
            }
        )
    return news_items       