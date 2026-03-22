import boto3
from botocore.exceptions import ClientError


def get_secret(secret_name: str) -> str:
    """Fetch a secret string from AWS Secrets Manager."""
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret '{secret_name}': {e}") from e
    return response["SecretString"]
