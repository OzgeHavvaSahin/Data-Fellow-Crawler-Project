import requests
from bs4 import BeautifulSoup

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
