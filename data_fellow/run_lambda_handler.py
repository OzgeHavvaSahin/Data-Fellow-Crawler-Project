from src.scraper import fetch_news, extract_links


def main():
    url = "https://news.google.com/topics/CAAqIggKIhxDQkFTRHdvSkwyMHZNREY2Ym1OZkVnSjBjaWdBUAE?hl=tr&gl=TR&ceid=TR%3Atr"
    soup = fetch_news(url)

    news_items = extract_links(soup)

    print(f"Found {len(news_items)} news items")

    for item in news_items[:10]:
        print("TITLE:", item["title"])
        print("URL:", item["url"])
        print("-" * 50)

if __name__ == "__main__":
    main()