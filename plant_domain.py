"""Plant care recommendation domain for the AO recommender demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


PLANT_TYPE_BITS = {
    "succulent": [0, 0, 0],
    "tropical": [0, 0, 1],
    "herb": [0, 1, 0],
    "flowering": [0, 1, 1],
    "fern": [1, 0, 0],
    "tree": [1, 0, 1],
}

LIGHT_BITS = {
    "low": [0, 0],
    "medium": [0, 1],
    "bright": [1, 1],
}

GOAL_BITS = {
    "easy-care": [0, 0],
    "faster-growth": [0, 1],
    "fix-symptoms": [1, 0],
    "harvest": [1, 1],
}


@dataclass(frozen=True)
class PlantCareAction:
    """A plant care action that can be recommended."""

    name: str
    plant_type: str
    light: str
    effort: str
    water_need: str
    minutes: int
    contexts: tuple[str, ...]
    description: str


PLANT_ACTIONS: tuple[PlantCareAction, ...] = (
    PlantCareAction("Check soil moisture before watering", "succulent", "bright", "low", "low", 5, ("easy-care", "fix-symptoms"), "Avoid overwatering by watering only when the top soil is dry."),
    PlantCareAction("Rotate the pot toward even light", "tropical", "medium", "low", "medium", 5, ("easy-care", "faster-growth"), "Turn the plant so new growth stays balanced instead of leaning toward a window."),
    PlantCareAction("Trim yellowing leaves", "tropical", "medium", "low", "medium", 10, ("fix-symptoms", "easy-care"), "Remove damaged foliage so the plant directs energy to healthy growth."),
    PlantCareAction("Prune basil above a leaf pair", "herb", "bright", "low", "medium", 10, ("harvest", "faster-growth"), "Harvest in a way that encourages branching and delays flowering."),
    PlantCareAction("Mist and inspect fern fronds", "fern", "low", "medium", "high", 15, ("fix-symptoms", "faster-growth"), "Raise local humidity and look for crispy edges or pest pressure."),
    PlantCareAction("Deadhead spent blooms", "flowering", "bright", "medium", "medium", 20, ("faster-growth", "easy-care"), "Remove fading flowers so the plant can keep producing new buds."),
    PlantCareAction("Top dress with compost", "tree", "bright", "medium", "medium", 25, ("faster-growth", "easy-care"), "Add a light nutrient boost without disturbing the root ball."),
    PlantCareAction("Flush mineral salts from soil", "tropical", "bright", "high", "high", 30, ("fix-symptoms", "faster-growth"), "Run water through the pot to remove fertilizer salts that can burn leaf tips."),
    PlantCareAction("Pinch mint runners back", "herb", "medium", "low", "medium", 10, ("harvest", "easy-care"), "Keep growth compact and encourage fresh edible leaves."),
    PlantCareAction("Move succulent closer to bright light", "succulent", "bright", "medium", "low", 15, ("fix-symptoms", "faster-growth"), "Reduce stretching by giving the plant stronger indirect light."),
    PlantCareAction("Check drainage and saucer water", "flowering", "medium", "low", "medium", 8, ("fix-symptoms", "easy-care"), "Prevent root rot by clearing standing water after watering."),
    PlantCareAction("Stake a leaning indoor tree", "tree", "medium", "medium", "medium", 20, ("fix-symptoms", "easy-care"), "Support the stem while you correct light direction and watering rhythm."),
)


def encode_plant_action(action: PlantCareAction, goal: str = "easy-care") -> list[int]:
    """Encode a plant care action plus user goal into the AO eight-bit input shape."""

    if action.plant_type not in PLANT_TYPE_BITS:
        raise ValueError(f"Unknown plant type: {action.plant_type}")
    if action.light not in LIGHT_BITS:
        raise ValueError(f"Unknown light level: {action.light}")
    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    high_effort_bit = [1 if action.effort == "high" else 0]
    return PLANT_TYPE_BITS[action.plant_type] + LIGHT_BITS[action.light] + high_effort_bit + GOAL_BITS[goal]


def score_plant_action(
    action: PlantCareAction,
    goal: str,
    minutes_available: int,
    indoor_light: str = "medium",
    feedback: dict[str, int] | None = None,
) -> int:
    """Score a plant action with deterministic plant-care preferences and feedback."""

    score = 0
    if goal in action.contexts:
        score += 35
    if action.minutes <= minutes_available:
        score += 20
    else:
        score -= (action.minutes - minutes_available) // 5 * 4
    if action.light == indoor_light:
        score += 16
    elif indoor_light == "bright" and action.light == "medium":
        score += 8
    if goal == "easy-care" and action.effort == "low":
        score += 14
    if goal == "fix-symptoms":
        score += 12
    if goal == "harvest" and action.plant_type == "herb":
        score += 18
    if action.water_need == "low" and goal == "easy-care":
        score += 8
    if feedback:
        score += feedback.get(action.name, 0) * 12
    return score


def recommend_plant_actions(
    goal: str = "easy-care",
    minutes_available: int = 15,
    indoor_light: str = "medium",
    feedback: dict[str, int] | None = None,
    actions: Iterable[PlantCareAction] = PLANT_ACTIONS,
    limit: int = 5,
) -> list[tuple[PlantCareAction, int]]:
    """Return plant care recommendations sorted from strongest to weakest match."""

    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")
    if indoor_light not in LIGHT_BITS:
        raise ValueError(f"Unknown light level: {indoor_light}")

    ranked = [
        (
            action,
            score_plant_action(
                action,
                goal=goal,
                minutes_available=minutes_available,
                indoor_light=indoor_light,
                feedback=feedback,
            ),
        )
        for action in actions
    ]
    ranked.sort(key=lambda item: (item[1], -item[0].minutes, item[0].name), reverse=True)
    return ranked[:limit]


def apply_feedback(
    feedback: dict[str, int] | None,
    action_name: str,
    liked: bool,
) -> dict[str, int]:
    """Return updated feedback weights for a plant care action."""

    updated = dict(feedback or {})
    updated[action_name] = updated.get(action_name, 0) + (1 if liked else -1)
    return updated
