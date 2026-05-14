"""Wellness micro-habit recommendation domain for the AO recommender demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


FOCUS_BITS = {
    "stress": [0, 0, 0],
    "sleep": [0, 0, 1],
    "focus": [0, 1, 0],
    "energy": [0, 1, 1],
    "connection": [1, 0, 0],
    "reflection": [1, 0, 1],
}

TIME_BITS = {
    "short": [0, 0],
    "medium": [0, 1],
    "long": [1, 1],
}

GOAL_BITS = {
    "calm": [0, 0],
    "better-sleep": [0, 1],
    "deep-work": [1, 0],
    "reset": [1, 1],
}


@dataclass(frozen=True)
class WellnessHabit:
    """A small wellness habit that can be recommended."""

    name: str
    focus: str
    time_bucket: str
    social: bool
    energy_level: str
    minutes: int
    contexts: tuple[str, ...]
    description: str


WELLNESS_HABITS: tuple[WellnessHabit, ...] = (
    WellnessHabit("Two-minute box breathing", "stress", "short", False, "low", 2, ("calm", "reset"), "Use a simple breathing cadence before a meeting or after context switching."),
    WellnessHabit("Write tomorrow's first task", "focus", "short", False, "low", 5, ("deep-work", "better-sleep"), "Close the day by choosing one concrete next action for tomorrow."),
    WellnessHabit("Screen-off wind-down block", "sleep", "medium", False, "low", 20, ("better-sleep", "calm"), "Create a low-stimulation buffer before bedtime."),
    WellnessHabit("Sunlight and water reset", "energy", "short", False, "medium", 10, ("reset", "deep-work"), "Step outside, hydrate, and give your attention a clean restart."),
    WellnessHabit("Focus sprint with phone away", "focus", "medium", False, "medium", 25, ("deep-work", "reset"), "Work on one task with notifications out of reach."),
    WellnessHabit("Send one appreciation note", "connection", "short", True, "low", 5, ("calm", "reset"), "Strengthen a relationship with a quick specific message."),
    WellnessHabit("Midday walk without audio", "reflection", "medium", False, "medium", 15, ("calm", "reset"), "Let your mind settle while moving at an easy pace."),
    WellnessHabit("Tidy one visible surface", "energy", "short", False, "medium", 8, ("reset", "deep-work"), "Remove one small source of visual friction from your workspace."),
    WellnessHabit("Guided body scan", "stress", "medium", False, "low", 12, ("calm", "better-sleep"), "Notice tension and relax one area at a time."),
    WellnessHabit("Plan a low-effort social check-in", "connection", "medium", True, "medium", 15, ("calm", "reset"), "Pick one person and one easy way to reconnect this week."),
    WellnessHabit("Evening reflection note", "reflection", "short", False, "low", 7, ("better-sleep", "calm"), "Write what worked today and what can be lighter tomorrow."),
    WellnessHabit("Long-form weekly reset", "reflection", "long", False, "medium", 35, ("reset", "deep-work"), "Review commitments, remove stale tasks, and choose the next week's focus."),
)


def encode_wellness_habit(habit: WellnessHabit, goal: str = "calm") -> list[int]:
    """Encode a wellness habit plus user goal into the AO eight-bit input shape."""

    if habit.focus not in FOCUS_BITS:
        raise ValueError(f"Unknown focus: {habit.focus}")
    if habit.time_bucket not in TIME_BITS:
        raise ValueError(f"Unknown time bucket: {habit.time_bucket}")
    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    social_bit = [1 if habit.social else 0]
    return FOCUS_BITS[habit.focus] + TIME_BITS[habit.time_bucket] + social_bit + GOAL_BITS[goal]


def score_wellness_habit(
    habit: WellnessHabit,
    goal: str,
    minutes_available: int,
    preferred_energy: str = "low",
    social_ok: bool = True,
    feedback: dict[str, int] | None = None,
) -> int:
    """Score a habit using deterministic context preferences plus feedback."""

    score = 0
    if goal in habit.contexts:
        score += 35
    if habit.minutes <= minutes_available:
        score += 20
    else:
        score -= (habit.minutes - minutes_available) // 5 * 5
    if habit.energy_level == preferred_energy:
        score += 14
    if not social_ok and habit.social:
        score -= 18
    if goal == "better-sleep" and habit.focus in {"sleep", "reflection", "stress"}:
        score += 12
    if goal == "deep-work" and habit.focus in {"focus", "energy"}:
        score += 12
    if goal == "calm" and habit.energy_level == "low":
        score += 8
    if feedback:
        score += feedback.get(habit.name, 0) * 12
    return score


def recommend_wellness_habits(
    goal: str = "calm",
    minutes_available: int = 15,
    preferred_energy: str = "low",
    social_ok: bool = True,
    feedback: dict[str, int] | None = None,
    habits: Iterable[WellnessHabit] = WELLNESS_HABITS,
    limit: int = 5,
) -> list[tuple[WellnessHabit, int]]:
    """Return wellness recommendations sorted from strongest to weakest match."""

    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")
    if preferred_energy not in {"low", "medium"}:
        raise ValueError(f"Unknown preferred energy: {preferred_energy}")

    ranked = [
        (
            habit,
            score_wellness_habit(
                habit,
                goal=goal,
                minutes_available=minutes_available,
                preferred_energy=preferred_energy,
                social_ok=social_ok,
                feedback=feedback,
            ),
        )
        for habit in habits
    ]
    ranked.sort(key=lambda item: (item[1], -item[0].minutes, item[0].name), reverse=True)
    return ranked[:limit]


def apply_feedback(
    feedback: dict[str, int] | None,
    habit_name: str,
    liked: bool,
) -> dict[str, int]:
    """Return updated feedback weights for a wellness habit."""

    updated = dict(feedback or {})
    updated[habit_name] = updated.get(habit_name, 0) + (1 if liked else -1)
    return updated
