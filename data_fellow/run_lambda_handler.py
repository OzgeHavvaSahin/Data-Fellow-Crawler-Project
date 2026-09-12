from src.scraper import fetch_news


def main():
    url = "https://news.google.com/"
    soup = fetch_news(url)

    # articles = soup.find_all("article")

    # print(f"Found {len(articles)} articles")

    # for article in articles[:5]:
    #     print(article.get_text(" ", strip=True))
    #     print("-" * 50)

    links = soup.find_all("a")

    print(f"Found {len(links)} links")

    for link in links[:30]:
        text = link.get_text(" ", strip=True)
        href = link.get("href")

        print("TEXT:", text)
        print("HREF:", href)
        print("-" * 50)

if __name__ == "__main__":
    main()