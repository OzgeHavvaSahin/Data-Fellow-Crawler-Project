from src.scraper import fetch_news, extract_links


def lambda_handler(event, context):
    category = "turkey"

    soup = fetch_news(category)
    news_items = extract_links(soup, category)

    return {
        "statusCode": 200,
        "category": category,
        "count": len(news_items),
        "articles": news_items[:10],
    }