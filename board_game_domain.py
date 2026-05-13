"""Board game domain data and deterministic recommendation logic.

The original demo uses an 8-bit AO input shape of [3, 2, 1, 2]. This module
keeps that shape while swapping the YouTube domain for a local board game
catalog and group-context inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


GAME_TYPES = [
    "strategy",
    "party",
    "cooperative",
    "family",
    "duel",
    "story",
    "puzzle",
    "economic",
]

DURATION_BUCKETS = ["quick", "standard", "long", "epic"]
TABLE_MOODS = ["casual", "competitive", "social", "immersive"]

BUCKET_MINUTES = {
    "quick": 30,
    "standard": 60,
    "long": 120,
    "epic": 180,
}


@dataclass(frozen=True)
class BoardGame:
    title: str
    game_type: str
    duration_bucket: str
    complexity: str
    interaction: str
    min_players: int
    max_players: int
    teach_minutes: int
    mood_tags: tuple[str, ...]
    best_for: str


BOARD_GAME_CATALOG = [
    BoardGame(
        title="Cascadia",
        game_type="family",
        duration_bucket="standard",
        complexity="light",
        interaction="low",
        min_players=1,
        max_players=4,
        teach_minutes=10,
        mood_tags=("casual", "puzzle"),
        best_for="relaxed tile-laying with low table friction",
    ),
    BoardGame(
        title="Codenames",
        game_type="party",
        duration_bucket="quick",
        complexity="light",
        interaction="high",
        min_players=4,
        max_players=8,
        teach_minutes=5,
        mood_tags=("social", "casual"),
        best_for="large groups that want fast wordplay",
    ),
    BoardGame(
        title="The Crew",
        game_type="cooperative",
        duration_bucket="quick",
        complexity="medium",
        interaction="medium",
        min_players=3,
        max_players=5,
        teach_minutes=10,
        mood_tags=("cooperative", "competitive"),
        best_for="quiet teamwork with escalating missions",
    ),
    BoardGame(
        title="Wingspan",
        game_type="strategy",
        duration_bucket="standard",
        complexity="medium",
        interaction="low",
        min_players=1,
        max_players=5,
        teach_minutes=15,
        mood_tags=("casual", "immersive"),
        best_for="engine building with a calm table feel",
    ),
    BoardGame(
        title="Root",
        game_type="strategy",
        duration_bucket="long",
        complexity="heavy",
        interaction="high",
        min_players=2,
        max_players=4,
        teach_minutes=30,
        mood_tags=("competitive", "immersive"),
        best_for="asymmetric conflict for experienced groups",
    ),
    BoardGame(
        title="7 Wonders",
        game_type="family",
        duration_bucket="standard",
        complexity="medium",
        interaction="medium",
        min_players=3,
        max_players=7,
        teach_minutes=15,
        mood_tags=("social", "competitive"),
        best_for="bigger tables that still want simultaneous turns",
    ),
    BoardGame(
        title="Azul",
        game_type="puzzle",
        duration_bucket="quick",
        complexity="light",
        interaction="medium",
        min_players=2,
        max_players=4,
        teach_minutes=8,
        mood_tags=("casual", "competitive"),
        best_for="short tactical drafting with clean rules",
    ),
    BoardGame(
        title="Dune: Imperium",
        game_type="economic",
        duration_bucket="long",
        complexity="heavy",
        interaction="medium",
        min_players=1,
        max_players=4,
        teach_minutes=25,
        mood_tags=("competitive", "immersive"),
        best_for="worker placement plus deck-building tension",
    ),
    BoardGame(
        title="Sherlock Holmes Consulting Detective",
        game_type="story",
        duration_bucket="long",
        complexity="medium",
        interaction="low",
        min_players=1,
        max_players=8,
        teach_minutes=10,
        mood_tags=("immersive", "casual"),
        best_for="group mystery-solving with note taking",
    ),
    BoardGame(
        title="Splendor Duel",
        game_type="duel",
        duration_bucket="quick",
        complexity="light",
        interaction="medium",
        min_players=2,
        max_players=2,
        teach_minutes=8,
        mood_tags=("competitive", "casual"),
        best_for="tight two-player tactical engine building",
    ),
    BoardGame(
        title="Just One",
        game_type="party",
        duration_bucket="quick",
        complexity="light",
        interaction="high",
        min_players=3,
        max_players=7,
        teach_minutes=3,
        mood_tags=("social", "casual"),
        best_for="zero-pressure cooperative guessing",
    ),
    BoardGame(
        title="Pandemic",
        game_type="cooperative",
        duration_bucket="standard",
        complexity="medium",
        interaction="high",
        min_players=2,
        max_players=4,
        teach_minutes=15,
        mood_tags=("cooperative", "immersive"),
        best_for="cooperative crisis management",
    ),
]


def _bits(value: int, width: int) -> list[int]:
    if value < 0 or value >= 2**width:
        raise ValueError(f"value {value} does not fit in {width} bits")
    return [(value >> shift) & 1 for shift in range(width - 1, -1, -1)]


def _index_or_default(values: list[str], value: str, default: str) -> int:
    return values.index(_choice_or_default(values, value, default))


def _choice_or_default(values: list[str], value: str, default: str) -> str:
    normalized = (value or default).lower()
    if normalized not in values:
        return default
    return normalized


def normalize_context(context: dict[str, Any] | None) -> dict[str, Any]:
    context = dict(context or {})
    players = int(context.get("players", 4))
    if players < 1:
        raise ValueError("players must be at least 1")

    available_minutes = int(context.get("available_minutes", 90))
    if available_minutes < 15:
        raise ValueError("available_minutes must be at least 15")

    return {
        "players": players,
        "available_minutes": available_minutes,
        "mood": _choice_or_default(
            TABLE_MOODS, str(context.get("mood", "casual")), "casual"
        ),
        "preferred_type": str(context.get("preferred_type", "")).lower(),
        "complexity": str(context.get("complexity", "any")).lower(),
        "social_energy": str(context.get("social_energy", "medium")).lower(),
        "want_teach_fast": bool(context.get("want_teach_fast", False)),
    }


def encode_game(game: BoardGame, context: dict[str, Any] | None = None) -> list[int]:
    """Encode a candidate game and group context into the AO [3, 2, 1, 2] shape."""

    normalized = normalize_context(context)
    type_bits = _bits(_index_or_default(GAME_TYPES, game.game_type, "family"), 3)
    duration_bits = _bits(
        _index_or_default(DURATION_BUCKETS, game.duration_bucket, "standard"), 2
    )
    interaction_bit = [1 if game.interaction == "high" else 0]
    mood_bits = _bits(_index_or_default(TABLE_MOODS, normalized["mood"], "casual"), 2)
    return type_bits + duration_bits + interaction_bit + mood_bits


def _feedback_adjustment(game: BoardGame, feedback: Iterable[dict[str, Any]] | None) -> float:
    if not feedback:
        return 0.0

    adjustment = 0.0
    for item in feedback:
        liked = bool(item.get("liked"))
        direction = 1.0 if liked else -1.0
        title = str(item.get("title", "")).lower()
        game_type = str(item.get("game_type", "")).lower()
        mood = str(item.get("mood", "")).lower()

        if title and title == game.title.lower():
            adjustment += direction * 4.0
        if game_type and game_type == game.game_type:
            adjustment += direction * 0.9
        if mood and mood in game.mood_tags:
            adjustment += direction * 0.4
    return adjustment


def _complexity_score(game_complexity: str, requested: str) -> float:
    if requested in ("", "any"):
        return 0.5
    if requested == game_complexity:
        return 2.0
    if requested == "medium" and game_complexity in ("light", "heavy"):
        return 0.5
    return -1.0


def score_game(
    game: BoardGame,
    context: dict[str, Any] | None = None,
    feedback: Iterable[dict[str, Any]] | None = None,
) -> float:
    normalized = normalize_context(context)
    if not (game.min_players <= normalized["players"] <= game.max_players):
        return -100.0

    game_minutes = BUCKET_MINUTES.get(game.duration_bucket)
    if game_minutes is None:
        return -100.0
    if game_minutes > normalized["available_minutes"]:
        return -100.0

    score = 1.0
    if normalized["preferred_type"] == game.game_type:
        score += 3.0
    elif not normalized["preferred_type"]:
        score += 0.5

    if normalized["mood"] in game.mood_tags:
        score += 2.2
    if normalized["mood"] == "social" and game.interaction == "high":
        score += 1.2
    if normalized["mood"] == "competitive" and game.interaction in ("medium", "high"):
        score += 0.8

    score += _complexity_score(game.complexity, normalized["complexity"])

    slack = normalized["available_minutes"] - game_minutes
    if 0 <= slack <= 30:
        score += 1.0
    elif slack > 60:
        score -= 0.5

    if normalized["social_energy"] == "high" and game.interaction == "high":
        score += 1.0
    if normalized["social_energy"] == "low" and game.interaction == "low":
        score += 1.0

    if normalized["want_teach_fast"]:
        score += 1.0 if game.teach_minutes <= 10 else -1.0

    score += _feedback_adjustment(game, feedback)
    return round(score, 3)


def explain_match(game: BoardGame, context: dict[str, Any]) -> str:
    normalized = normalize_context(context)
    reasons = []
    if normalized["mood"] in game.mood_tags:
        reasons.append(f"fits a {normalized['mood']} table")
    if normalized["preferred_type"] == game.game_type:
        reasons.append(f"matches {game.game_type} preference")
    if game.teach_minutes <= 10:
        reasons.append("quick to teach")
    if game.interaction == "high":
        reasons.append("high table interaction")
    if not reasons:
        reasons.append(game.best_for)
    return "; ".join(reasons)


def recommend_games(
    context: dict[str, Any] | None = None,
    limit: int = 5,
    feedback: Iterable[dict[str, Any]] | None = None,
    catalog: Iterable[BoardGame] = BOARD_GAME_CATALOG,
) -> list[dict[str, Any]]:
    normalized = normalize_context(context)
    scored = []
    for game in catalog:
        score = score_game(game, normalized, feedback)
        if score <= -99:
            continue
        scored.append(
            {
                "title": game.title,
                "score": score,
                "game_type": game.game_type,
                "duration_bucket": game.duration_bucket,
                "complexity": game.complexity,
                "players": f"{game.min_players}-{game.max_players}",
                "binary_input": encode_game(game, normalized),
                "best_for": game.best_for,
                "reason": explain_match(game, normalized),
            }
        )

    scored.sort(key=lambda row: (-row["score"], row["title"]))
    return scored[:limit]


def format_recommendations(recommendations: list[dict[str, Any]]) -> str:
    lines = []
    for index, item in enumerate(recommendations, start=1):
        bits = "".join(str(bit) for bit in item["binary_input"])
        lines.append(
            f"{index}. {item['title']} ({item['score']}) - {item['reason']} "
            f"[bits={bits}]"
        )
    return "\n".join(lines)
