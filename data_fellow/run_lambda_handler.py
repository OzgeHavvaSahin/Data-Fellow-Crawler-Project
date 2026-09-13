from src.lambda_func import lambda_handler


def main():
    result = lambda_handler(None, None)

    print("STATUS:", result["statusCode"])
    print("-" * 50)

    for item in result["results"]:
        print("CATEGORY:", item["category"])
        print("COUNT:", item["count"])
        print("S3 KEY:", item["s3_key"])
        print("-" * 50)


if __name__ == "__main__":
    main()