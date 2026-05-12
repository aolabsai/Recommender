"""Travel-experience domain logic for the AO Labs recommender bounty.

The Streamlit demo imports this module, and the tests exercise it without
requiring Streamlit or private AO packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


BUDGET_ORDER = {"free": 0, "low": 1, "medium": 2, "high": 3}
ACTIVITY_BITS = {
    "culture": [0, 0, 0],
    "food": [0, 0, 1],
    "nature": [0, 1, 0],
    "history": [0, 1, 1],
    "nightlife": [1, 0, 0],
    "wellness": [1, 0, 1],
    "family": [1, 1, 0],
    "adventure": [1, 1, 1],
}
BUDGET_BITS = {
    "free": [0, 0],
    "low": [0, 1],
    "medium": [1, 0],
    "high": [1, 1],
}
MOOD_BITS = {
    "relaxed": [0, 0],
    "curious": [0, 1],
    "active": [1, 0],
    "social": [1, 1],
}
MOOD_ACTIVITY_WEIGHTS = {
    "relaxed": {"wellness": 3, "nature": 2, "culture": 1},
    "curious": {"culture": 3, "history": 3, "food": 1},
    "active": {"adventure": 3, "nature": 2, "family": 1},
    "social": {"nightlife": 3, "food": 2, "culture": 1},
}
PACE_SCORE = {"calm": 0, "balanced": 1, "energetic": 2}


@dataclass(frozen=True)
class TravelExperience:
    id: str
    name: str
    city: str
    country: str
    activity_type: str
    budget: str
    outdoor: bool
    pace: str
    party: tuple[str, ...]
    duration_hours: float
    description: str


@dataclass(frozen=True)
class TravelPreferences:
    mood: str = "curious"
    max_budget: str = "medium"
    pace: str = "balanced"
    party: str = "solo"


CATALOG: tuple[TravelExperience, ...] = (
    TravelExperience(
        id="lisbon-azulejo-walk",
        name="Azulejo street-art and tile walk",
        city="Lisbon",
        country="Portugal",
        activity_type="culture",
        budget="low",
        outdoor=True,
        pace="balanced",
        party=("solo", "couple", "group"),
        duration_hours=2.5,
        description="A self-guided walk through Alfama and Mouraria tilework, murals, and viewpoints.",
    ),
    TravelExperience(
        id="tokyo-depachika-dinner",
        name="Depachika tasting loop",
        city="Tokyo",
        country="Japan",
        activity_type="food",
        budget="medium",
        outdoor=False,
        pace="calm",
        party=("solo", "couple", "family"),
        duration_hours=1.5,
        description="Sample seasonal bento, wagashi, and regional snacks in a department-store food hall.",
    ),
    TravelExperience(
        id="reykjavik-geothermal-dip",
        name="Neighborhood geothermal pool reset",
        city="Reykjavik",
        country="Iceland",
        activity_type="wellness",
        budget="low",
        outdoor=True,
        pace="calm",
        party=("solo", "couple", "family"),
        duration_hours=2,
        description="A low-key soak circuit at a local pool with hot pots and cold plunge options.",
    ),
    TravelExperience(
        id="barcelona-gothic-legends",
        name="Gothic Quarter legends route",
        city="Barcelona",
        country="Spain",
        activity_type="history",
        budget="free",
        outdoor=True,
        pace="balanced",
        party=("solo", "couple", "group"),
        duration_hours=2,
        description="A compact route connecting Roman walls, medieval courtyards, and local legends.",
    ),
    TravelExperience(
        id="vancouver-stanley-bike",
        name="Stanley Park seawall ride",
        city="Vancouver",
        country="Canada",
        activity_type="nature",
        budget="medium",
        outdoor=True,
        pace="energetic",
        party=("solo", "couple", "family", "group"),
        duration_hours=3,
        description="Cycle the seawall with forest detours, beach stops, and mountain views.",
    ),
    TravelExperience(
        id="mexico-city-lucha-night",
        name="Lucha libre and late taco crawl",
        city="Mexico City",
        country="Mexico",
        activity_type="nightlife",
        budget="medium",
        outdoor=False,
        pace="energetic",
        party=("couple", "group"),
        duration_hours=4,
        description="A high-energy evening pairing an arena match with nearby al pastor stands.",
    ),
    TravelExperience(
        id="copenhagen-harbor-swim",
        name="Harbor swim and sauna hour",
        city="Copenhagen",
        country="Denmark",
        activity_type="wellness",
        budget="medium",
        outdoor=True,
        pace="calm",
        party=("solo", "couple", "group"),
        duration_hours=2,
        description="A relaxed swim-sauna session near the harbor baths with cafe options nearby.",
    ),
    TravelExperience(
        id="queenstown-canyon-swing",
        name="Canyon swing adrenaline slot",
        city="Queenstown",
        country="New Zealand",
        activity_type="adventure",
        budget="high",
        outdoor=True,
        pace="energetic",
        party=("solo", "couple", "group"),
        duration_hours=3,
        description="A guided canyon swing session for travelers chasing a memorable, high-intensity day.",
    ),
    TravelExperience(
        id="london-museum-kids",
        name="Hands-on museum morning",
        city="London",
        country="United Kingdom",
        activity_type="family",
        budget="free",
        outdoor=False,
        pace="calm",
        party=("family",),
        duration_hours=3,
        description="A child-friendly museum route with interactive galleries and quiet reset spaces.",
    ),
    TravelExperience(
        id="marrakesh-souk-cooking",
        name="Souk pantry and tagine workshop",
        city="Marrakesh",
        country="Morocco",
        activity_type="food",
        budget="medium",
        outdoor=True,
        pace="balanced",
        party=("solo", "couple", "family", "group"),
        duration_hours=4,
        description="Shop spices in the souk, then cook a tagine with a local host.",
    ),
    TravelExperience(
        id="athens-acropolis-sunrise",
        name="Acropolis sunrise history walk",
        city="Athens",
        country="Greece",
        activity_type="history",
        budget="low",
        outdoor=True,
        pace="balanced",
        party=("solo", "couple", "family", "group"),
        duration_hours=2.5,
        description="Beat the heat with an early route around the Acropolis and surrounding viewpoints.",
    ),
    TravelExperience(
        id="seoul-han-river-picnic",
        name="Han River picnic and ramen stop",
        city="Seoul",
        country="South Korea",
        activity_type="family",
        budget="low",
        outdoor=True,
        pace="calm",
        party=("solo", "couple", "family", "group"),
        duration_hours=2,
        description="A flexible riverside picnic with convenience-store ramen and skyline views.",
    ),
    TravelExperience(
        id="berlin-techno-intro",
        name="Low-pressure club culture intro",
        city="Berlin",
        country="Germany",
        activity_type="nightlife",
        budget="medium",
        outdoor=False,
        pace="energetic",
        party=("solo", "couple", "group"),
        duration_hours=5,
        description="A beginner-friendly evening plan for sampling Berlin's electronic music scene.",
    ),
    TravelExperience(
        id="banff-lake-hike",
        name="Alpine lake early hike",
        city="Banff",
        country="Canada",
        activity_type="nature",
        budget="low",
        outdoor=True,
        pace="energetic",
        party=("solo", "couple", "group"),
        duration_hours=4,
        description="An early-start trail plan for lake views before the crowds arrive.",
    ),
)


def encode_experience(experience: TravelExperience, preferences: TravelPreferences) -> list[int]:
    """Return the eight-bit AO input used by the travel demo.

    Bits are grouped as: activity type (3), budget (2), outdoor flag (1), mood (2).
    That shape intentionally matches the original demo architecture:
    ``arch_i = [3, 2, 1, 2]``.
    """

    return (
        ACTIVITY_BITS[experience.activity_type]
        + BUDGET_BITS[experience.budget]
        + [1 if experience.outdoor else 0]
        + MOOD_BITS[preferences.mood]
    )


def budget_allows(experience: TravelExperience, max_budget: str) -> bool:
    return BUDGET_ORDER[experience.budget] <= BUDGET_ORDER[max_budget]


def score_experience(
    experience: TravelExperience,
    preferences: TravelPreferences,
    positive_feedback: Iterable[str] = (),
    negative_feedback: Iterable[str] = (),
) -> tuple[int, list[str]]:
    """Score a catalog item and explain the strongest matching reasons."""

    positive = set(positive_feedback)
    negative = set(negative_feedback)
    score = 0
    reasons: list[str] = []

    if budget_allows(experience, preferences.max_budget):
        score += 5
        reasons.append(f"fits {preferences.max_budget} budget")
    else:
        score -= 6
        reasons.append(f"above {preferences.max_budget} budget")

    mood_weight = MOOD_ACTIVITY_WEIGHTS[preferences.mood].get(experience.activity_type, 0)
    if mood_weight:
        score += mood_weight
        reasons.append(f"{experience.activity_type} works for a {preferences.mood} mood")

    pace_delta = abs(PACE_SCORE[experience.pace] - PACE_SCORE[preferences.pace])
    score += max(0, 3 - pace_delta)
    if pace_delta == 0:
        reasons.append(f"{experience.pace} pace match")

    if preferences.party in experience.party:
        score += 3
        reasons.append(f"good for {preferences.party} travel")

    if experience.id in positive:
        score += 6
        reasons.append("you asked for more like this")
    if experience.activity_type in positive:
        score += 3
        reasons.append(f"learned positive signal for {experience.activity_type}")
    if experience.id in negative:
        score -= 8
        reasons.append("you asked to see less like this")
    if experience.activity_type in negative:
        score -= 4
        reasons.append(f"learned negative signal for {experience.activity_type}")

    return score, reasons[:4]


def rank_experiences(
    catalog: Sequence[TravelExperience],
    preferences: TravelPreferences,
    positive_feedback: Iterable[str] = (),
    negative_feedback: Iterable[str] = (),
) -> list[tuple[TravelExperience, int, list[str]]]:
    ranked = [
        (
            experience,
            *score_experience(
                experience,
                preferences,
                positive_feedback=positive_feedback,
                negative_feedback=negative_feedback,
            ),
        )
        for experience in catalog
    ]
    return sorted(ranked, key=lambda item: (item[1], item[0].name), reverse=True)


def recommendation_percentage(score: int) -> int:
    """Convert fallback score into a UI-friendly percentage."""

    return max(0, min(100, 45 + score * 5))
