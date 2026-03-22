import time
from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr


def get_table(table_name: str):
    """Return a DynamoDB Table resource."""
    dynamodb = boto3.resource("dynamodb")
    return dynamodb.Table(table_name)


def get_cached(table, key: str) -> dict | None:
    """
    Retrieve a cached item by media_id.
    Returns None on miss or if the item's TTL has expired.
    """
    response = table.get_item(Key={"media_id": key})
    item = response.get("Item")
    if item is None:
        return None
    # Guard against items where TTL hasn't been purged yet by DynamoDB
    if item.get("ttl", 0) < int(time.time()):
        return None
    return item


def set_cached(table, key: str, value: dict[str, Any], ttl_days: int = 30) -> None:
    """
    Store an item in the cache with a TTL of ttl_days days from now.
    The item is keyed by media_id and includes the provided value fields.
    """
    ttl = int(time.time()) + ttl_days * 86400
    item = {"media_id": key, "ttl": ttl, **value}
    table.put_item(Item=item)
