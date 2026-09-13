import json
import boto3

from src.config import S3_BUCKET, AWS_REGION

s3_client = boto3.client("s3" , region_name= AWS_REGION)

def save_to_s3(data,key):
    s3_client.put_object(
        Bucket = S3_BUCKET,
        Key = key,
        Body = json.dumps(data, ensure_ascii= False),
        ContentType = "application/json"
    )