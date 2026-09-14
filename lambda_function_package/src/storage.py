import json
import boto3
from datetime import datetime, timezone

from src.config import S3_BUCKET, AWS_REGION

s3_client = boto3.client("s3" , region_name= AWS_REGION)

def save_to_s3(data,category):
    now = datetime.now(timezone.utc)

    key = (
        f"news/{category}/"
        f"{now.year}/"
        f"{now.month:02d}/"
        f"{now.day:02d}/"
        f"{now.hour:02d}-{now.minute:02d}.json"
    )

    s3_client.put_object(
        Bucket = S3_BUCKET,
        Key = key,
        Body = json.dumps(data, ensure_ascii= False,
                          indent=2),
        ContentType = "application/json"
    )
    return key