import json
import boto3


s3 = boto3.client("s3")


def read_articles_from_s3(bucket, key):
    response = s3.get_object(
        Bucket=bucket,
        Key=key
    )

    body = response["Body"].read().decode("utf-8")

    return json.loads(body)