from src.lambda_func import lambda_handler


def main():
    result = lambda_handler(None, None)

    print("STATUS:", result["statusCode"])
    print("CATEGORY:", result["category"])
    print("COUNT:", result["count"])
    print("S3 KEY:", result["s3_key"])

    print("-" * 50)

    for article in result["articles"]:
        print("RANK:", article["rank"])
        print("TITLE:", article["title"])
        print("DESCRIPTION:", article["description"])
        print("SOURCE:", article["source"])
        print("PUBLISHED AT:", article["published_at"])
        print("URL:", article["url"])
        print("-" * 50)


if __name__ == "__main__":
    main()