"""Career and job-search recommendation domain for the AO recommender demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


TRACK_BITS = {
    "resume": [0, 0, 0],
    "networking": [0, 0, 1],
    "interview": [0, 1, 0],
    "skills": [0, 1, 1],
    "search": [1, 0, 0],
    "negotiation": [1, 0, 1],
}

TIME_BITS = {
    "quick": [0, 0],
    "focused": [0, 1],
    "deep": [1, 1],
}

GOAL_BITS = {
    "first-role": [0, 0],
    "switch-career": [0, 1],
    "level-up": [1, 0],
    "restart-search": [1, 1],
}


@dataclass(frozen=True)
class CareerAction:
    """A job-search or career-growth action that can be recommended."""

    name: str
    track: str
    time_commitment: str
    confidence_need: str
    remote_friendly: bool
    weekly_hours: int
    contexts: tuple[str, ...]
    description: str


CAREER_ACTIONS: tuple[CareerAction, ...] = (
    CareerAction("Rewrite resume around three measurable wins", "resume", "focused", "medium", True, 3, ("first-role", "restart-search", "level-up"), "Turn role bullets into outcome-focused proof points before applying."),
    CareerAction("Create a targeted company shortlist", "search", "quick", "low", True, 2, ("restart-search", "switch-career"), "Pick ten companies that match your constraints before sending applications."),
    CareerAction("Schedule two warm intro conversations", "networking", "focused", "medium", True, 3, ("switch-career", "level-up"), "Ask people near your target role for short, specific learning conversations."),
    CareerAction("Build a role-specific portfolio case study", "skills", "deep", "high", True, 6, ("first-role", "switch-career", "level-up"), "Show one realistic project with problem, decisions, tradeoffs, and results."),
    CareerAction("Practice behavioral stories with STAR notes", "interview", "focused", "medium", True, 3, ("first-role", "restart-search"), "Prepare concise examples for conflict, ambiguity, impact, and learning."),
    CareerAction("Run a mock technical interview loop", "interview", "deep", "high", True, 5, ("level-up", "restart-search"), "Simulate the full interview flow and capture concrete gaps to practice."),
    CareerAction("Learn one missing tool through a mini project", "skills", "deep", "medium", True, 5, ("switch-career", "first-role"), "Pick one tool repeatedly found in target job posts and ship a small artifact."),
    CareerAction("Send five tailored applications", "search", "focused", "low", True, 4, ("restart-search", "first-role"), "Apply only where the resume and cover note can name a clear fit."),
    CareerAction("Audit compensation bands before interviews", "negotiation", "quick", "medium", True, 2, ("level-up", "switch-career"), "Collect market salary data so expectations are anchored before offers arrive."),
    CareerAction("Draft a negotiation script", "negotiation", "focused", "high", True, 3, ("level-up",), "Prepare a respectful counteroffer script based on role scope and market data."),
    CareerAction("Refresh LinkedIn headline and featured work", "resume", "quick", "low", True, 1, ("restart-search", "switch-career", "level-up"), "Make your target role and strongest proof visible before outreach."),
    CareerAction("Join a focused hiring community", "networking", "quick", "low", True, 2, ("first-role", "switch-career"), "Find a small community where target-role hiring posts and referrals appear."),
)


def encode_career_action(action: CareerAction, goal: str = "restart-search") -> list[int]:
    """Encode an action plus career goal into the AO eight-bit input shape."""

    if action.track not in TRACK_BITS:
        raise ValueError(f"Unknown track: {action.track}")
    if action.time_commitment not in TIME_BITS:
        raise ValueError(f"Unknown time commitment: {action.time_commitment}")
    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    confidence_bit = [1 if action.confidence_need == "high" else 0]
    return TRACK_BITS[action.track] + TIME_BITS[action.time_commitment] + confidence_bit + GOAL_BITS[goal]


def score_career_action(
    action: CareerAction,
    goal: str,
    weekly_hours_available: int,
    wants_remote: bool = True,
    feedback: dict[str, int] | None = None,
) -> int:
    """Score an action with deterministic context preferences and optional feedback."""

    score = 0
    if goal in action.contexts:
        score += 35
    if action.weekly_hours <= weekly_hours_available:
        score += 20
    else:
        score -= (action.weekly_hours - weekly_hours_available) * 8
    if action.time_commitment == "quick":
        score += 12
    elif action.time_commitment == "focused":
        score += 8
    if wants_remote and action.remote_friendly:
        score += 8
    if goal == "first-role" and action.track in {"resume", "skills", "search"}:
        score += 12
    if goal == "level-up" and action.track in {"interview", "negotiation"}:
        score += 15
    if goal == "switch-career" and action.track in {"networking", "skills"}:
        score += 14
    if feedback:
        score += feedback.get(action.name, 0) * 12
    return score


def recommend_career_actions(
    goal: str = "restart-search",
    weekly_hours_available: int = 4,
    wants_remote: bool = True,
    feedback: dict[str, int] | None = None,
    actions: Iterable[CareerAction] = CAREER_ACTIONS,
    limit: int = 5,
) -> list[tuple[CareerAction, int]]:
    """Return career recommendations sorted from strongest to weakest match."""

    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    ranked = [
        (
            action,
            score_career_action(
                action,
                goal=goal,
                weekly_hours_available=weekly_hours_available,
                wants_remote=wants_remote,
                feedback=feedback,
            ),
        )
        for action in actions
    ]
    ranked.sort(key=lambda item: (item[1], -item[0].weekly_hours, item[0].name), reverse=True)
    return ranked[:limit]


def apply_feedback(
    feedback: dict[str, int] | None,
    action_name: str,
    liked: bool,
) -> dict[str, int]:
    """Return updated feedback weights for a career action."""

    updated = dict(feedback or {})
    updated[action_name] = updated.get(action_name, 0) + (1 if liked else -1)
    return updated
