import os

from helpers.s3_reader import read_json


def get_travel_reviews(location: str = "") -> dict:
    """
    Return Tarun's travel destination reviews.

    Args:
        location: Optional filter string. If provided, only reviews whose
                  place field contains this string (case-insensitive) are returned.

    Returns:
        {"reviews": [...]} where each review has keys:
        place, country, rating, review, date, highlights
    """
    bucket = os.environ["DATA_BUCKET"]
    reviews: list = read_json(bucket, "travel_reviews.json")

    if location:
        needle = location.lower()
        reviews = [r for r in reviews if needle in r.get("place", "").lower()]

    return {"reviews": reviews}
