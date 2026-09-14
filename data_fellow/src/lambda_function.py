from src.scraper import fetch_news, extract_links
from src.storage import save_to_s3
from src.config import URLS


def lambda_handler(event, context):
    results = []

    for category in URLS:
        if category == "base":
            continue

        root = fetch_news(category)
        news_items = extract_links(root, category)


        s3_key = save_to_s3(
            news_items,
            category
        )

        results.append(
            {
                "category": category,
                "count": len(news_items),
                "s3_key": s3_key,
            }
        )

    return {
        "statusCode": 200,
        "results": results,
    }