import base64
import os

import anthropic
import httpx

from helpers.cache import get_cached, get_table, set_cached
from helpers.secrets import get_secret

INSTAGRAM_API_URL = (
    "https://graph.instagram.com/me/media"
    "?fields=id,caption,media_url,permalink,timestamp,media_type"
    "&access_token={token}"
)
VISION_PROMPT = (
    "Describe this photo in 2-3 sentences capturing Tarun's photography style "
    "and subject matter. Caption context: {caption}"
)
MAX_IMAGES = 5


def _summarize_image(media_url: str, caption: str) -> str:
    """Download an image and ask Claude claude-opus-4-5 to describe it."""
    image_bytes = httpx.get(media_url, timeout=15).content
    b64_image = base64.standard_b64encode(image_bytes).decode("utf-8")

    # Detect content type from URL extension; default to jpeg
    url_lower = media_url.lower().split("?")[0]
    if url_lower.endswith(".png"):
        media_type = "image/png"
    elif url_lower.endswith(".webp"):
        media_type = "image/webp"
    elif url_lower.endswith(".gif"):
        media_type = "image/gif"
    else:
        media_type = "image/jpeg"

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": b64_image,
                        },
                    },
                    {
                        "type": "text",
                        "text": VISION_PROMPT.format(caption=caption or "(no caption)"),
                    },
                ],
            }
        ],
    )
    return message.content[0].text


def get_photography(topic: str = "") -> list:
    """
    Return Tarun's Instagram photography with AI-generated summaries.

    Args:
        topic: Optional filter string applied case-insensitively to image captions.

    Returns:
        List of up to 5 dicts: {permalink, timestamp, caption, summary}
    """
    token = get_secret("tarun/instagram-token")
    url = INSTAGRAM_API_URL.format(token=token)

    response = httpx.get(url, timeout=15)
    response.raise_for_status()
    media_items: list = response.json().get("data", [])

    # Keep only IMAGE type
    images = [m for m in media_items if m.get("media_type") == "IMAGE"]

    # Filter by topic if provided
    if topic:
        needle = topic.lower()
        images = [
            m for m in images if needle in (m.get("caption") or "").lower()
        ]

    images = images[:MAX_IMAGES]

    cache_table_name = os.environ.get("CACHE_TABLE", "")
    table = get_table(cache_table_name) if cache_table_name else None

    results = []
    for item in images:
        media_id = item["id"]
        caption = item.get("caption", "")

        summary = None
        if table is not None:
            cached = get_cached(table, media_id)
            if cached:
                summary = cached.get("summary")

        if summary is None:
            summary = _summarize_image(item["media_url"], caption)
            if table is not None:
                set_cached(table, media_id, {"summary": summary})

        results.append(
            {
                "permalink": item.get("permalink"),
                "timestamp": item.get("timestamp"),
                "caption": caption,
                "summary": summary,
            }
        )

    return results
