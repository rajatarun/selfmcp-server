import os

from helpers.s3_reader import read_json


def get_hiking_activity(trail_name: str = "") -> dict:
    """
    Return Tarun's hiking trail records.

    Args:
        trail_name: Optional filter string. If provided, only trails whose
                    name contains this string (case-insensitive) are returned.

    Returns:
        {"trails": [...]} where each trail has keys:
        name, distance_miles, elevation_ft, date, rating, notes
    """
    bucket = os.environ["DATA_BUCKET"]
    trails: list = read_json(bucket, "hiking_data.json")

    if trail_name:
        needle = trail_name.lower()
        trails = [t for t in trails if needle in t.get("name", "").lower()]

    return {"trails": trails}
