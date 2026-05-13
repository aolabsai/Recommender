"""Personal finance recommendation domain for the AO recommender demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


FOCUS_BITS = {
    "savings": [0, 0, 0],
    "debt": [0, 0, 1],
    "investing": [0, 1, 0],
    "cash-flow": [0, 1, 1],
    "protection": [1, 0, 0],
}

HORIZON_BITS = {
    "now": [0, 0],
    "short": [0, 1],
    "long": [1, 1],
}

GOAL_BITS = {
    "build-buffer": [0, 0],
    "reduce-stress": [0, 1],
    "grow-wealth": [1, 0],
    "simplify": [1, 1],
}


@dataclass(frozen=True)
class FinanceAction:
    """A financial habit or action that can be recommended."""

    name: str
    focus: str
    horizon: str
    effort: str
    risk: str
    monthly_cash_impact: int
    contexts: tuple[str, ...]
    description: str


FINANCE_ACTIONS: tuple[FinanceAction, ...] = (
    FinanceAction(
        name="Start a starter emergency fund",
        focus="savings",
        horizon="short",
        effort="medium",
        risk="low",
        monthly_cash_impact=150,
        contexts=("build-buffer", "reduce-stress"),
        description="Automatically move a small fixed amount into a separate emergency account.",
    ),
    FinanceAction(
        name="Audit recurring subscriptions",
        focus="cash-flow",
        horizon="now",
        effort="low",
        risk="low",
        monthly_cash_impact=45,
        contexts=("simplify", "reduce-stress"),
        description="Cancel or downgrade subscriptions that no longer support current priorities.",
    ),
    FinanceAction(
        name="Snowball the smallest debt",
        focus="debt",
        horizon="short",
        effort="medium",
        risk="low",
        monthly_cash_impact=100,
        contexts=("reduce-stress", "simplify"),
        description="Pay minimums on every debt and send extra cash to the smallest balance.",
    ),
    FinanceAction(
        name="Refinance high-interest debt",
        focus="debt",
        horizon="short",
        effort="high",
        risk="medium",
        monthly_cash_impact=120,
        contexts=("reduce-stress", "build-buffer"),
        description="Compare lower-rate options before interest costs crowd out other goals.",
    ),
    FinanceAction(
        name="Increase retirement contribution by one percent",
        focus="investing",
        horizon="long",
        effort="low",
        risk="medium",
        monthly_cash_impact=-60,
        contexts=("grow-wealth", "simplify"),
        description="Make a small automatic retirement increase that compounds quietly over time.",
    ),
    FinanceAction(
        name="Build a low-cost index fund habit",
        focus="investing",
        horizon="long",
        effort="medium",
        risk="medium",
        monthly_cash_impact=-100,
        contexts=("grow-wealth", "build-buffer"),
        description="Use recurring purchases into diversified, low-fee index funds.",
    ),
    FinanceAction(
        name="Create a weekly cash-flow checkpoint",
        focus="cash-flow",
        horizon="now",
        effort="low",
        risk="low",
        monthly_cash_impact=80,
        contexts=("simplify", "reduce-stress"),
        description="Review upcoming bills, income, and spending once a week.",
    ),
    FinanceAction(
        name="Negotiate bills and insurance renewals",
        focus="cash-flow",
        horizon="short",
        effort="medium",
        risk="low",
        monthly_cash_impact=70,
        contexts=("simplify", "build-buffer"),
        description="Ask providers for retention discounts or compare quotes before renewals.",
    ),
    FinanceAction(
        name="Set a one-month bill buffer",
        focus="protection",
        horizon="long",
        effort="high",
        risk="low",
        monthly_cash_impact=250,
        contexts=("build-buffer", "reduce-stress"),
        description="Accumulate enough cash so next month's fixed bills are already covered.",
    ),
    FinanceAction(
        name="Review insurance deductibles",
        focus="protection",
        horizon="short",
        effort="medium",
        risk="medium",
        monthly_cash_impact=35,
        contexts=("reduce-stress", "build-buffer"),
        description="Match deductibles to cash reserves so premiums and risk stay balanced.",
    ),
    FinanceAction(
        name="Create a values-based spending rule",
        focus="cash-flow",
        horizon="now",
        effort="low",
        risk="low",
        monthly_cash_impact=60,
        contexts=("simplify", "grow-wealth"),
        description="Define what spending is always worth it and what gets paused by default.",
    ),
    FinanceAction(
        name="Start a side-income experiment",
        focus="savings",
        horizon="short",
        effort="high",
        risk="medium",
        monthly_cash_impact=200,
        contexts=("grow-wealth", "build-buffer"),
        description="Run a small, time-boxed income experiment before committing heavily.",
    ),
)


def encode_finance_action(action: FinanceAction, goal: str = "build-buffer") -> list[int]:
    """Encode an action plus user goal into the AO eight-bit input shape."""

    if action.focus not in FOCUS_BITS:
        raise ValueError(f"Unknown focus: {action.focus}")
    if action.horizon not in HORIZON_BITS:
        raise ValueError(f"Unknown horizon: {action.horizon}")
    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    risk_bit = [1 if action.risk == "medium" else 0]
    return FOCUS_BITS[action.focus] + HORIZON_BITS[action.horizon] + risk_bit + GOAL_BITS[goal]


def score_finance_action(
    action: FinanceAction,
    goal: str,
    available_cash: int,
    feedback: dict[str, int] | None = None,
) -> int:
    """Score an action using deterministic preferences and optional feedback."""

    score = 0

    if goal in action.contexts:
        score += 35

    if action.monthly_cash_impact > 0:
        score += min(action.monthly_cash_impact // 10, 25)
    elif available_cash >= abs(action.monthly_cash_impact):
        score += 15
    else:
        score -= 20

    if action.effort == "low":
        score += 15
    elif action.effort == "medium":
        score += 8

    if goal == "grow-wealth" and action.focus == "investing":
        score += 20
    if goal == "reduce-stress" and action.risk == "low":
        score += 10

    if feedback:
        score += feedback.get(action.name, 0) * 12

    return score


def recommend_finance_actions(
    goal: str = "build-buffer",
    available_cash: int = 100,
    feedback: dict[str, int] | None = None,
    limit: int = 3,
    actions: Iterable[FinanceAction] = FINANCE_ACTIONS,
) -> list[tuple[FinanceAction, int]]:
    """Return the highest-scoring finance actions for the user's current context."""

    if goal not in GOAL_BITS:
        raise ValueError(f"Unknown goal: {goal}")

    ranked = [
        (action, score_finance_action(action, goal, available_cash, feedback))
        for action in actions
    ]
    ranked.sort(key=lambda item: (item[1], item[0].monthly_cash_impact, item[0].name), reverse=True)
    return ranked[:limit]


def apply_feedback(feedback: dict[str, int], action_name: str, liked: bool) -> dict[str, int]:
    """Return updated feedback weights for a finance action."""

    updated = dict(feedback)
    updated[action_name] = updated.get(action_name, 0) + (1 if liked else -1)
    return updated
