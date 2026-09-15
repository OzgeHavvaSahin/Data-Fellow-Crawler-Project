from s3_reader import read_articles_from_s3
from database import save_articles


def lambda_handler(event, context):
    record = event["Records"][0]

    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    articles = read_articles_from_s3(
        bucket,
        key
    )

    save_articles(articles)

    return {
        "statusCode": 200,
        "message": "Articles inserted successfully",
        "count": len(articles),
        "s3_key": key
    }