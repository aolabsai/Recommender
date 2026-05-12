"""Fitness/workout domain helpers for the AO Labs recommender demo.

This module is intentionally dependency-free so reviewers can validate the
domain mapping and fallback recommendations without private AO packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


GOALS = ("strength", "cardio", "mobility", "recovery")
INTENSITIES = ("low", "medium", "high")
EQUIPMENT = ("none", "dumbbells", "bands", "machine")
ENERGY_LEVELS = ("low", "medium", "high")

INPUT_SCHEMA = [
    ("workout_goal", len(GOALS)),
    ("workout_intensity", len(INTENSITIES)),
    ("workout_duration_bucket", 2),
    ("workout_equipment", len(EQUIPMENT)),
    ("user_goal", len(GOALS)),
    ("user_energy", len(ENERGY_LEVELS)),
    ("user_time_budget_bucket", 2),
    ("user_equipment", len(EQUIPMENT)),
]

INPUT_WIDTH = sum(width for _, width in INPUT_SCHEMA)


@dataclass(frozen=True)
class Workout:
    id: str
    title: str
    goal: str
    intensity: str
    duration_min: int
    equipment: str
    format: str
    context_tags: tuple[str, ...]
    description: str


WORKOUT_CATALOG: tuple[Workout, ...] = (
    Workout(
        id="desk-reset-mobility",
        title="Desk Reset Mobility Flow",
        goal="mobility",
        intensity="low",
        duration_min=12,
        equipment="none",
        format="flow",
        context_tags=("work-break", "stiff", "travel"),
        description="Neck, thoracic, hip, and ankle mobility for stiff desk days.",
    ),
    Workout(
        id="dumbbell-full-body",
        title="30-Minute Dumbbell Full Body",
        goal="strength",
        intensity="medium",
        duration_min=30,
        equipment="dumbbells",
        format="circuit",
        context_tags=("home", "balanced", "muscle"),
        description="Squat, hinge, push, pull, and carry circuit with moderate rest.",
    ),
    Workout(
        id="bodyweight-strength",
        title="No-Equipment Strength Ladder",
        goal="strength",
        intensity="medium",
        duration_min=24,
        equipment="none",
        format="ladder",
        context_tags=("travel", "home", "minimal"),
        description="Push-up, split-squat, plank, and glute bridge ladder.",
    ),
    Workout(
        id="quick-hiit",
        title="18-Minute Low-Space HIIT",
        goal="cardio",
        intensity="high",
        duration_min=18,
        equipment="none",
        format="interval",
        context_tags=("energized", "short", "sweat"),
        description="Low-space intervals using skaters, fast feet, squats, and marches.",
    ),
    Workout(
        id="zone-two-bike",
        title="Zone 2 Bike Builder",
        goal="cardio",
        intensity="medium",
        duration_min=45,
        equipment="machine",
        format="steady",
        context_tags=("endurance", "focused", "recovery-safe"),
        description="Steady aerobic bike ride with conversational pacing guidance.",
    ),
    Workout(
        id="band-posterior-chain",
        title="Band Posterior Chain Primer",
        goal="strength",
        intensity="low",
        duration_min=20,
        equipment="bands",
        format="circuit",
        context_tags=("warmup", "glutes", "back"),
        description="Band pull-aparts, hinges, rows, and glute activation work.",
    ),
    Workout(
        id="evening-downshift",
        title="Evening Downshift Recovery",
        goal="recovery",
        intensity="low",
        duration_min=15,
        equipment="none",
        format="flow",
        context_tags=("stressed", "evening", "sleep"),
        description="Breathing, gentle mobility, and long exhale holds for downshifting.",
    ),
    Workout(
        id="treadmill-threshold",
        title="Treadmill Threshold Intervals",
        goal="cardio",
        intensity="high",
        duration_min=35,
        equipment="machine",
        format="interval",
        context_tags=("race-prep", "focused", "sweat"),
        description="Progressive threshold blocks with easy recoveries.",
    ),
    Workout(
        id="dumbbell-upper",
        title="Upper Body Dumbbell Density",
        goal="strength",
        intensity="high",
        duration_min=28,
        equipment="dumbbells",
        format="density",
        context_tags=("muscle", "short", "focused"),
        description="Timed push/pull supersets with strict rest caps.",
    ),
    Workout(
        id="runner-mobility",
        title="Runner Hips and Calves Mobility",
        goal="mobility",
        intensity="low",
        duration_min=18,
        equipment="bands",
        format="flow",
        context_tags=("running", "stiff", "prehab"),
        description="Banded hip openers, calf eccentrics, and ankle range work.",
    ),
    Workout(
        id="machine-recovery-row",
        title="Easy Row Recovery Flush",
        goal="recovery",
        intensity="low",
        duration_min=25,
        equipment="machine",
        format="steady",
        context_tags=("sore", "easy", "endurance"),
        description="Low-rate row with nasal breathing and mobility cooldown.",
    ),
    Workout(
        id="band-cardio-boxing",
        title="Band-Resisted Cardio Boxing",
        goal="cardio",
        intensity="medium",
        duration_min=22,
        equipment="bands",
        format="interval",
        context_tags=("fun", "home", "coordination"),
        description="Shadow boxing intervals with light band resistance.",
    ),
)


DEFAULT_CONTEXT = {
    "goal": "strength",
    "energy": "medium",
    "time_budget_min": 30,
    "equipment": "none",
}


def _one_hot(value: str, options: tuple[str, ...]) -> list[int]:
    normalized = value.lower().strip()
    if normalized not in options:
        normalized = options[0]
    return [1 if option == normalized else 0 for option in options]


def _duration_bucket(minutes: int) -> list[int]:
    if minutes <= 15:
        return [0, 0]
    if minutes <= 30:
        return [0, 1]
    if minutes <= 45:
        return [1, 0]
    return [1, 1]


def normalize_context(context: dict | None = None) -> dict:
    values = {**DEFAULT_CONTEXT, **(context or {})}
    goal = str(values.get("goal", DEFAULT_CONTEXT["goal"])).lower().strip()
    energy = str(values.get("energy", DEFAULT_CONTEXT["energy"])).lower().strip()
    equipment = str(values.get("equipment", DEFAULT_CONTEXT["equipment"])).lower().strip()
    try:
        time_budget_min = int(values.get("time_budget_min", DEFAULT_CONTEXT["time_budget_min"]))
    except (TypeError, ValueError):
        time_budget_min = DEFAULT_CONTEXT["time_budget_min"]

    return {
        "goal": goal if goal in GOALS else DEFAULT_CONTEXT["goal"],
        "energy": energy if energy in ENERGY_LEVELS else DEFAULT_CONTEXT["energy"],
        "time_budget_min": max(5, time_budget_min),
        "equipment": equipment if equipment in EQUIPMENT else DEFAULT_CONTEXT["equipment"],
    }


def encode_workout(workout: Workout, context: dict | None = None) -> list[int]:
    user_context = normalize_context(context)
    encoded = (
        _one_hot(workout.goal, GOALS)
        + _one_hot(workout.intensity, INTENSITIES)
        + _duration_bucket(workout.duration_min)
        + _one_hot(workout.equipment, EQUIPMENT)
        + _one_hot(user_context["goal"], GOALS)
        + _one_hot(user_context["energy"], ENERGY_LEVELS)
        + _duration_bucket(user_context["time_budget_min"])
        + _one_hot(user_context["equipment"], EQUIPMENT)
    )
    if len(encoded) != INPUT_WIDTH:
        raise ValueError(f"encoded input has width {len(encoded)}, expected {INPUT_WIDTH}")
    return encoded


def score_workout(workout: Workout, context: dict | None = None) -> int:
    user_context = normalize_context(context)
    score = 0

    if workout.goal == user_context["goal"]:
        score += 40
    if workout.duration_min <= user_context["time_budget_min"]:
        score += 20
    else:
        score -= min(20, workout.duration_min - user_context["time_budget_min"])

    if workout.equipment == user_context["equipment"]:
        score += 25
    elif workout.equipment == "none":
        score += 15
    else:
        score -= 15

    intensity_rank = {name: index for index, name in enumerate(INTENSITIES)}
    energy_rank = {name: index for index, name in enumerate(ENERGY_LEVELS)}
    intensity_gap = abs(intensity_rank[workout.intensity] - energy_rank[user_context["energy"]])
    score += max(0, 15 - (intensity_gap * 8))

    if user_context["energy"] in workout.context_tags:
        score += 5

    return score


def recommend_workouts(
    context: dict | None = None,
    *,
    limit: int = 5,
    catalog: Iterable[Workout] = WORKOUT_CATALOG,
) -> list[tuple[Workout, int, list[int]]]:
    ranked = [
        (workout, score_workout(workout, context), encode_workout(workout, context))
        for workout in catalog
    ]
    ranked.sort(key=lambda item: (item[1], -item[0].duration_min, item[0].title), reverse=True)
    return ranked[:limit]
