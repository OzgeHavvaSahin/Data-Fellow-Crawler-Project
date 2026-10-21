import json
import boto3
from datetime import datetime, timezone

from src.config import S3_BUCKET, AWS_REGION

s3_client = boto3.client("s3", region_name=AWS_REGION)


def save_to_s3(data, category):
    now = datetime.now(timezone.utc)

    if not isinstance(data, list):
        raise ValueError("Haber verisi liste olmalıdır.")

    if not data:
        return None

    key = (
        f"news/category={category}/"
        f"year={now.year}/"
        f"month={now.month:02d}/"
        f"day={now.day:02d}/"
        f"{now.hour:02d}-{now.minute:02d}.jsonl"
    )

    jsonl_data = "\n".join(
        json.dumps(
            {k: v for k, v in article.items() if k != "category"},
            ensure_ascii=False
        )
        for article in data
    ) + "\n"

    s3_client.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=jsonl_data.encode("utf-8"),
        ContentType="application/x-ndjson"
    )

    return key
