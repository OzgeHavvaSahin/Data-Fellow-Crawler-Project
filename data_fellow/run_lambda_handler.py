from src.scraper import fetch_news, extract_links


def main():
    category = "turkey"

    soup = fetch_news(category)

    news_items = extract_links(soup, category)

    print(f"Found {len(news_items)} news items")

    for rank, item in enumerate(news_items[:10], start=1):
        print("CATEGORY:", item["category"])
        print("RANK:", rank)
        print("TITLE:", item["title"])
        print("URL:", item["url"])
        print("-" * 50)

if __name__ == "__main__":
    main()