FACTS: dict[str, str | dict] = {
    "photography": (
        "Tarun is an avid mobile and mirrorless photographer who focuses on landscape, "
        "street, and nature photography. He shoots primarily with a Sony A7C and iPhone 15 Pro. "
        "His style leans toward golden-hour landscapes, candid urban moments, and macro nature shots. "
        "He has been featured on Instagram's Explore page multiple times and maintains a feed of "
        "curated travel and outdoor photography with a muted, film-inspired edit style."
    ),
    "hiking": (
        "Tarun is an avid hiker with over 200 miles logged across Texas, the American Southwest, "
        "and international trails. He prefers technical day hikes with significant elevation gain "
        "and panoramic summit views. Favorite parks include Big Bend, Zion, and the Texas Hill "
        "Country. He tracks all hikes with a Garmin Fenix 7 and documents them on AllTrails. "
        "Goal for 2025: complete all major trails in Big Bend National Park."
    ),
    "travel": (
        "Tarun has visited 28 countries across 5 continents, with a deep focus on immersive "
        "cultural travel rather than resort stays. He prioritizes food, local markets, historical "
        "sites, and off-the-beaten-path neighborhoods. Top destinations: Japan, Mexico (especially "
        "Oaxaca), Portugal, Morocco, and India. He travels 4-6 times per year and documents "
        "detailed reviews of every destination visited. Next planned trip: Patagonia, Chile."
    ),
    "work": (
        "Tarun Raja is a Senior Lead Software Engineer and AI Architect at JPMorgan Chase, "
        "based in the Dallas-Fort Worth area. He leads AI/ML platform engineering initiatives "
        "with a focus on large language model integration, agentic systems, and developer tooling "
        "for enterprise-scale applications. He has 10+ years of experience in distributed systems, "
        "cloud-native architecture (primarily AWS), and Python/Java backend development. "
        "He is a frequent speaker at internal tech conferences and an advocate for responsible "
        "AI deployment in financial services."
    ),
}


def get_personal_facts(category: str = "") -> dict:
    """
    Return personal facts about Tarun Raja.

    Args:
        category: One of 'photography', 'hiking', 'travel', 'work'.
                  If empty or unrecognized, all categories are returned.
    """
    normalized = category.strip().lower()
    if normalized in FACTS:
        return {normalized: FACTS[normalized]}
    return dict(FACTS)
