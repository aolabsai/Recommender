from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


TOPIC_BUCKETS = {
    "python": 0,
    "machine learning": 1,
    "data engineering": 2,
    "frontend": 3,
    "product": 4,
    "systems": 5,
    "security": 6,
    "design": 7,
}

FORMAT_BUCKETS = {
    "article": 0,
    "video": 1,
    "course": 2,
    "project": 3,
}

LEARNING_GOALS = {
    "surprise me": [0, 0],
    "ship a prototype": [0, 1],
    "deepen fundamentals": [1, 0],
    "prepare for interview": [1, 1],
}


@dataclass(frozen=True)
class LearningResourceCandidate:
    title: str
    provider: str
    topics: Tuple[str, ...]
    format: str
    duration_minutes: int
    difficulty: str
    hands_on: bool
    free: bool
    summary: str


LEARNING_CATALOG: Tuple[LearningResourceCandidate, ...] = (
    LearningResourceCandidate(
        "Build a FastAPI Notes API",
        "Practical Python Lab",
        ("python", "systems"),
        "project",
        75,
        "intermediate",
        True,
        True,
        "Implement CRUD routes, validation, and a small pytest suite.",
    ),
    LearningResourceCandidate(
        "Embeddings for Product Search",
        "Vector School",
        ("machine learning", "product"),
        "course",
        180,
        "intermediate",
        True,
        False,
        "Design a semantic search prototype with evaluation notes.",
    ),
    LearningResourceCandidate(
        "SQL Window Functions by Example",
        "Data Notebook",
        ("data engineering",),
        "article",
        35,
        "beginner",
        True,
        True,
        "Hands-on ranking, rolling aggregates, and cohort queries.",
    ),
    LearningResourceCandidate(
        "React Server Components Mental Model",
        "Frontend Field Guide",
        ("frontend", "systems"),
        "video",
        48,
        "advanced",
        False,
        True,
        "A visual walkthrough of server/client boundaries and data flow.",
    ),
    LearningResourceCandidate(
        "Threat Modeling a Small SaaS",
        "Secure Build Notes",
        ("security", "product"),
        "project",
        95,
        "intermediate",
        True,
        True,
        "Map assets, trust boundaries, and abuse cases for a starter app.",
    ),
    LearningResourceCandidate(
        "Design Systems for Data-Dense Tools",
        "Interface Workshop",
        ("design", "product"),
        "course",
        150,
        "intermediate",
        True,
        False,
        "Turn dashboards into scannable, reusable interface patterns.",
    ),
    LearningResourceCandidate(
        "Async Python Under Load",
        "Backend Bench",
        ("python", "systems"),
        "article",
        55,
        "advanced",
        True,
        True,
        "Profile event-loop stalls and compare queueing strategies.",
    ),
    LearningResourceCandidate(
        "Data Pipeline Reliability Checklist",
        "Warehouse Weekly",
        ("data engineering", "systems"),
        "article",
        28,
        "beginner",
        False,
        True,
        "A compact guide to retries, idempotency, and data quality checks.",
    ),
    LearningResourceCandidate(
        "Machine Learning Interview Drills",
        "Model Prep",
        ("machine learning",),
        "video",
        65,
        "advanced",
        False,
        False,
        "Practice feature engineering, metrics, and model tradeoff questions.",
    ),
    LearningResourceCandidate(
        "Prototype a Pricing Page in Svelte",
        "Launch UI Lab",
        ("frontend", "design"),
        "project",
        70,
        "beginner",
        True,
        True,
        "Build a responsive pricing page with accessible controls.",
    ),
    LearningResourceCandidate(
        "Product Metrics That Survive Contact",
        "PM Systems",
        ("product", "data engineering"),
        "article",
        42,
        "intermediate",
        False,
        True,
        "Define activation, retention, and revenue metrics that resist vanity.",
    ),
    LearningResourceCandidate(
        "Secure OAuth Redirects",
        "Auth Clinic",
        ("security", "systems"),
        "course",
        120,
        "advanced",
        True,
        False,
        "Harden redirect URI validation, PKCE, and token storage decisions.",
    ),
)


def to_bits(value: int, width: int) -> List[int]:
    if value < 0:
        raise ValueError("value must be non-negative")
    if value >= 2**width:
        raise ValueError("value does not fit in requested bit width")
    return [int(bit) for bit in format(value, f"0{width}b")]


def normalize_goal(goal: str) -> str:
    normalized = goal.strip().lower()
    if normalized not in LEARNING_GOALS:
        return "surprise me"
    return normalized


def primary_topic(resource: LearningResourceCandidate) -> str:
    for topic in resource.topics:
        if topic in TOPIC_BUCKETS:
            return topic
    return "python"


def duration_bucket(duration_minutes: int) -> int:
    if duration_minutes < 45:
        return 0
    if duration_minutes < 90:
        return 1
    if duration_minutes < 180:
        return 2
    return 3


def difficulty_bucket(difficulty: str) -> int:
    return 1 if difficulty.strip().lower() in {"advanced", "expert"} else 0


def encode_learning_resource(
    resource: LearningResourceCandidate,
    goal: str,
) -> List[int]:
    return (
        to_bits(TOPIC_BUCKETS[primary_topic(resource)], 3)
        + to_bits(FORMAT_BUCKETS.get(resource.format, 0), 2)
        + to_bits(duration_bucket(resource.duration_minutes), 2)
        + [difficulty_bucket(resource.difficulty)]
        + [1 if resource.hands_on else 0]
        + [1 if resource.free else 0]
        + LEARNING_GOALS[normalize_goal(goal)]
    )


def recommendation_percentage(agent_output: Sequence[int]) -> int:
    if not agent_output:
        return 0
    positive = sum(1 for value in agent_output if value == 1)
    return round((positive / len(agent_output)) * 100)


def pick_next_learning_resource(
    seen_titles: Iterable[str],
    index_seed: int = 0,
) -> LearningResourceCandidate:
    seen = set(seen_titles)
    unseen = [resource for resource in LEARNING_CATALOG if resource.title not in seen]
    candidates = unseen or list(LEARNING_CATALOG)
    return candidates[index_seed % len(candidates)]


def format_learning_card(resource: LearningResourceCandidate) -> str:
    topics = ", ".join(resource.topics)
    format_text = resource.format.title()
    hands_on_text = "hands-on" if resource.hands_on else "conceptual"
    price_text = "free" if resource.free else "paid"
    return (
        f"**{resource.title}** by {resource.provider}\n\n"
        f"{format_text} | {topics} | {resource.duration_minutes} min | "
        f"{resource.difficulty} | {hands_on_text} | {price_text}\n\n"
        f"{resource.summary}"
    )
