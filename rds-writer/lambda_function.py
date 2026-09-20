from s3_reader import read_articles_from_s3
from database import save_articles , get_article_count


def lambda_handler(event, context):
    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    articles = read_articles_from_s3(
        bucket,
        key
    )

    save_articles(articles)

    total_count = get_article_count()

    print(f"S3 key: {key}")
    print(f"Inserted article count: {len(articles)}")
    print(f"Total article count: {total_count}")

    return {
        "statusCode": 200,
        "message": "Articles inserted successfully",
        "count": len(articles),
        "total_article_count": total_count,
        "s3_key": key
    }