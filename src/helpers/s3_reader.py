import json

import boto3
from botocore.exceptions import ClientError


def read_json(bucket: str, key: str) -> list:
    """Download and parse a JSON file from S3. Returns a list."""
    client = boto3.client("s3")
    try:
        response = client.get_object(Bucket=bucket, Key=key)
    except ClientError as e:
        raise RuntimeError(f"Failed to read s3://{bucket}/{key}: {e}") from e
    body = response["Body"].read()
    return json.loads(body)
