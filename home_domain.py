"""Home maintenance recommendation domain for the AO recommender demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


CATEGORY_BITS = {
    "safety": [0, 0, 0],
    "energy": [0, 0, 1],
    "plumbing": [0, 1, 0],
    "appliance": [0, 1, 1],
    "cleaning": [1, 0, 0],
    "seasonal": [1, 0, 1],
}

URGENCY_BITS = {
    "routine": [0, 0],
    "soon": [0, 1],
    "urgent": [1, 1],
}

GOAL_BITS = {
    "safety": [0, 0],
    "save-money": [0, 1],
    "prevent-breakdowns": [1, 0],
    "clean-comfort": [1, 1],
}


@dataclass(frozen=True)
class HomeTask:
    """A household upkeep task that can be recommended."""

    name: str
    category: str
    urgency: str
    effort: str
    cost_tier: str
    minutes: int
    contexts: tuple[str, ...]
    description: str


HOME_TASKS: tuple[HomeTask, ...] = (
    HomeTask("Test smoke and carbon monoxide alarms", "safety", "routine", "low", "free", 15, ("safety", "prevent-breakdowns"), "Confirm alarms work and replace weak batteries before they become an emergency."),
    HomeTask("Replace HVAC filter", "energy", "soon", "low", "low", 20, ("save-money", "prevent-breakdowns"), "Improve airflow, reduce energy waste, and protect the heating or cooling system."),
    HomeTask("Flush sediment from the water heater", "plumbing", "soon", "medium", "free", 45, ("prevent-breakdowns", "save-money"), "Drain sediment so the heater runs efficiently and is less likely to fail early."),
    HomeTask("Clean refrigerator condenser coils", "appliance", "routine", "medium", "free", 35, ("save-money", "prevent-breakdowns"), "Remove dust from the coils so the compressor does not work harder than needed."),
    HomeTask("Seal drafts around doors and windows", "energy", "soon", "medium", "low", 60, ("save-money", "clean-comfort"), "Use weatherstripping or caulk to reduce drafts and stabilize room temperature."),
    HomeTask("Inspect under-sink plumbing for leaks", "plumbing", "routine", "low", "free", 20, ("safety", "prevent-breakdowns"), "Catch slow leaks before they damage cabinets, flooring, or walls."),
    HomeTask("Deep-clean dryer lint path", "safety", "urgent", "medium", "free", 40, ("safety", "save-money"), "Clear lint from the trap, hose, and vent path to reduce fire risk and improve drying time."),
    HomeTask("Descale shower heads and faucets", "cleaning", "routine", "low", "low", 30, ("clean-comfort", "save-money"), "Remove mineral buildup to improve water flow and keep fixtures looking fresh."),
    HomeTask("Clean gutters before heavy rain", "seasonal", "urgent", "high", "free", 90, ("prevent-breakdowns", "safety"), "Prevent overflow that can damage fascia, siding, foundations, or basements."),
    HomeTask("Vacuum bathroom exhaust fan grille", "cleaning", "routine", "low", "free", 15, ("clean-comfort", "prevent-breakdowns"), "Restore ventilation so humidity leaves the room more quickly."),
    HomeTask("Check appliance hoses for bulges or cracks", "appliance", "soon", "low", "free", 20, ("safety", "prevent-breakdowns"), "Inspect washer, dishwasher, and ice-maker lines for early signs of failure."),
    HomeTask("Build a seasonal maintenance checklist", "seasonal", "routine", "medium", "free", 45, ("prevent-breakdowns", "clean-comfort"), "Create a simple recurring plan so small tasks do not become expensive repairs."),
)


def encode_home_task(task: HomeTask, goal: str = "prevent-breakdowns") -> list[int]:
    """Encode a home task plus household goal into the AO eight-bit input shape."""

    if task.category not in CATEGORY_BITS:
        raise ValueError(f"Unknown category: {task.category}")
    if task.urgency not in URGENCY_BITS:
        raise ValueError(f"Unknown urgency: {task.urgency}")
    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    high_effort_bit = [1 if task.effort == "high" else 0]
    return CATEGORY_BITS[task.category] + URGENCY_BITS[task.urgency] + high_effort_bit + GOAL_BITS[goal]


def score_home_task(
    task: HomeTask,
    goal: str,
    minutes_available: int,
    prefer_low_cost: bool = True,
    feedback: dict[str, int] | None = None,
) -> int:
    """Score a home task with deterministic context preferences and optional feedback."""

    score = 0
    if goal in task.contexts:
        score += 35
    if task.minutes <= minutes_available:
        score += 20
    else:
        score -= (task.minutes - minutes_available) // 5 * 4
    if task.urgency == "urgent":
        score += 16
    elif task.urgency == "soon":
        score += 10
    if prefer_low_cost and task.cost_tier in {"free", "low"}:
        score += 10
    if goal == "safety" and task.category == "safety":
        score += 18
    if goal == "save-money" and task.category in {"energy", "appliance"}:
        score += 14
    if goal == "clean-comfort" and task.category == "cleaning":
        score += 14
    if feedback:
        score += feedback.get(task.name, 0) * 12
    return score


def recommend_home_tasks(
    goal: str = "prevent-breakdowns",
    minutes_available: int = 45,
    prefer_low_cost: bool = True,
    feedback: dict[str, int] | None = None,
    tasks: Iterable[HomeTask] = HOME_TASKS,
    limit: int = 5,
) -> list[tuple[HomeTask, int]]:
    """Return household upkeep recommendations sorted from strongest to weakest match."""

    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    ranked = [
        (
            task,
            score_home_task(
                task,
                goal=goal,
                minutes_available=minutes_available,
                prefer_low_cost=prefer_low_cost,
                feedback=feedback,
            ),
        )
        for task in tasks
    ]
    ranked.sort(key=lambda item: (item[1], -item[0].minutes, item[0].name), reverse=True)
    return ranked[:limit]


def apply_feedback(
    feedback: dict[str, int] | None,
    task_name: str,
    liked: bool,
) -> dict[str, int]:
    """Return updated feedback weights for a home maintenance task."""

    updated = dict(feedback or {})
    updated[task_name] = updated.get(task_name, 0) + (1 if liked else -1)
    return updated
