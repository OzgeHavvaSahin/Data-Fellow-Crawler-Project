from src.scraper import fetch_news, extract_links
from src.storage import save_to_s3


def lambda_handler(event, context):
    category = "turkey"

    soup = fetch_news(category)
    news_items = extract_links(soup, category)

    first_10_articles = news_items[:10]

    s3_key = save_to_s3(
        first_10_articles,
        category
    )

    return {
        "statusCode": 200,
        "category": category,
        "count": len(first_10_articles),
        "s3_key": s3_key,
        "articles": first_10_articles,
    }