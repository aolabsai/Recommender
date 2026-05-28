"""Open-source issue recommendation domain for the AO recommender demo."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


AREA_BITS = {
    "frontend": [0, 0, 0],
    "backend": [0, 0, 1],
    "docs": [0, 1, 0],
    "testing": [0, 1, 1],
    "devops": [1, 0, 0],
    "data": [1, 0, 1],
    "cli": [1, 1, 0],
}

EFFORT_BITS = {
    "small": [0, 0],
    "medium": [0, 1],
    "large": [1, 1],
}

GOAL_BITS = {
    "learn": [0, 0],
    "quick-win": [0, 1],
    "portfolio": [1, 0],
    "maintainer-impact": [1, 1],
}

EFFORT_RANK = {"small": 0, "medium": 1, "large": 2}


@dataclass(frozen=True)
class IssueCandidate:
    """A local issue-like work item that can be recommended to a contributor."""

    id: str
    title: str
    area: str
    effort: str
    beginner_friendly: bool
    goals: tuple[str, ...]
    stack: tuple[str, ...]
    risk: str
    description: str


ISSUE_CATALOG: tuple[IssueCandidate, ...] = (
    IssueCandidate(
        id="keyboard-navigation-audit",
        title="Fix keyboard navigation gaps in the settings panel",
        area="frontend",
        effort="small",
        beginner_friendly=True,
        goals=("learn", "quick-win", "portfolio"),
        stack=("react", "accessibility", "css"),
        risk="low",
        description="Audit tab order, focus rings, and escape handling in a compact UI panel.",
    ),
    IssueCandidate(
        id="flaky-date-parser-test",
        title="Add regression coverage for locale-sensitive date parsing",
        area="testing",
        effort="small",
        beginner_friendly=True,
        goals=("learn", "quick-win"),
        stack=("python", "parser", "unittest"),
        risk="low",
        description="Capture known date edge cases and protect the parser from locale drift.",
    ),
    IssueCandidate(
        id="api-pagination-bounds",
        title="Clamp API pagination bounds and document defaults",
        area="backend",
        effort="small",
        beginner_friendly=True,
        goals=("quick-win", "maintainer-impact"),
        stack=("typescript", "api", "validation"),
        risk="low",
        description="Reject negative pages, cap page size, and make pagination behavior explicit.",
    ),
    IssueCandidate(
        id="docker-healthcheck",
        title="Add Docker healthcheck and startup diagnostics",
        area="devops",
        effort="medium",
        beginner_friendly=False,
        goals=("portfolio", "maintainer-impact"),
        stack=("docker", "bash", "ci"),
        risk="medium",
        description="Expose a lightweight health endpoint and wire container health status to it.",
    ),
    IssueCandidate(
        id="docs-install-paths",
        title="Clarify install paths for Windows, macOS, and Linux",
        area="docs",
        effort="small",
        beginner_friendly=True,
        goals=("learn", "quick-win"),
        stack=("markdown", "docs"),
        risk="low",
        description="Replace ambiguous setup instructions with verified platform-specific paths.",
    ),
    IssueCandidate(
        id="csv-import-memory",
        title="Stream large CSV imports without loading the whole file",
        area="data",
        effort="medium",
        beginner_friendly=False,
        goals=("portfolio", "maintainer-impact"),
        stack=("python", "csv", "performance"),
        risk="medium",
        description="Process rows incrementally and report malformed rows without aborting the batch.",
    ),
    IssueCandidate(
        id="cli-config-precedence",
        title="Make CLI config precedence deterministic",
        area="cli",
        effort="medium",
        beginner_friendly=False,
        goals=("portfolio", "maintainer-impact"),
        stack=("node", "cli", "config"),
        risk="medium",
        description="Define and test precedence across flags, environment variables, and config files.",
    ),
    IssueCandidate(
        id="storybook-empty-state",
        title="Add empty-state stories for data-heavy components",
        area="frontend",
        effort="small",
        beginner_friendly=True,
        goals=("learn", "portfolio", "quick-win"),
        stack=("react", "storybook", "css"),
        risk="low",
        description="Show loading, empty, error, and populated states for reusable dashboard widgets.",
    ),
    IssueCandidate(
        id="scheduler-race-condition",
        title="Prevent duplicate background jobs after rapid restarts",
        area="backend",
        effort="large",
        beginner_friendly=False,
        goals=("portfolio", "maintainer-impact"),
        stack=("python", "scheduler", "database"),
        risk="high",
        description="Guard job leases with durable ownership so restarts cannot enqueue duplicates.",
    ),
    IssueCandidate(
        id="ci-cache-split",
        title="Split CI caches by lockfile and runtime version",
        area="devops",
        effort="medium",
        beginner_friendly=True,
        goals=("quick-win", "maintainer-impact"),
        stack=("github-actions", "ci", "node"),
        risk="low",
        description="Avoid stale dependency restores by keying caches on lockfiles and runtime versions.",
    ),
    IssueCandidate(
        id="benchmark-data-fixture",
        title="Add a small benchmark fixture for import performance",
        area="data",
        effort="small",
        beginner_friendly=True,
        goals=("learn", "quick-win", "portfolio"),
        stack=("python", "benchmark", "csv"),
        risk="low",
        description="Provide deterministic fixture data and a repeatable timing harness for imports.",
    ),
    IssueCandidate(
        id="upgrade-guide-mdx",
        title="Write a migration guide for the new component API",
        area="docs",
        effort="medium",
        beginner_friendly=True,
        goals=("portfolio", "maintainer-impact"),
        stack=("mdx", "docs", "react"),
        risk="low",
        description="Explain breaking changes with before/after snippets and a checklist for maintainers.",
    ),
)


def get_issue_by_id(issue_id: str) -> IssueCandidate:
    """Return a catalog issue by id."""

    for issue in ISSUE_CATALOG:
        if issue.id == issue_id:
            return issue
    raise ValueError(f"Unknown issue id: {issue_id}")


def encode_issue(issue: IssueCandidate, goal: str = "quick-win") -> list[int]:
    """Encode an issue plus contributor goal into the AO eight-bit input shape."""

    _validate_option("area", issue.area, AREA_BITS)
    _validate_option("effort", issue.effort, EFFORT_BITS)
    _validate_option("goal", goal, GOAL_BITS)

    beginner_bit = [1 if issue.beginner_friendly else 0]
    return AREA_BITS[issue.area] + EFFORT_BITS[issue.effort] + beginner_bit + GOAL_BITS[goal]


def rank_issues(
    preferred_area: str = "any",
    effort_budget: str = "medium",
    contributor_level: str = "intermediate",
    wants_beginner_friendly: bool = False,
    goal: str = "quick-win",
    stack: Iterable[str] | None = None,
    feedback: Iterable[dict[str, object]] | None = None,
    limit: int = 5,
) -> list[dict[str, object]]:
    """Rank catalog issues for a contributor profile and optional prior feedback."""

    if preferred_area != "any":
        _validate_option("preferred_area", preferred_area, AREA_BITS)
    _validate_option("effort_budget", effort_budget, EFFORT_BITS)
    _validate_option("goal", goal, GOAL_BITS)
    if contributor_level not in {"new", "intermediate", "experienced"}:
        raise ValueError(f"Unknown contributor_level: {contributor_level}")
    if limit < 1:
        raise ValueError("limit must be at least 1")

    desired_stack = {item.lower() for item in (stack or [])}
    feedback_items = list(feedback or [])
    budget_rank = EFFORT_RANK[effort_budget]
    ranked = []

    for issue in ISSUE_CATALOG:
        score = 0
        if preferred_area == "any":
            score += 1
        elif issue.area == preferred_area:
            score += 5

        if EFFORT_RANK[issue.effort] <= budget_rank:
            score += 3
        else:
            score -= 4

        if goal in issue.goals:
            score += 4
        if issue.risk == "low":
            score += 2
        elif issue.risk == "high":
            score -= 3

        if wants_beginner_friendly and issue.beginner_friendly:
            score += 3
        if contributor_level == "new" and issue.beginner_friendly:
            score += 2
        if contributor_level == "experienced" and issue.effort in {"medium", "large"}:
            score += 1

        score += 2 * len(desired_stack.intersection(issue.stack))
        score += _feedback_score(issue, feedback_items)

        ranked.append(
            {
                "id": issue.id,
                "title": issue.title,
                "area": issue.area,
                "effort": issue.effort,
                "beginner_friendly": issue.beginner_friendly,
                "goals": issue.goals,
                "stack": issue.stack,
                "risk": issue.risk,
                "description": issue.description,
                "binary_input": encode_issue(issue, goal=goal),
                "score": score,
            }
        )

    ranked.sort(key=lambda item: (-int(item["score"]), str(item["id"])))
    return ranked[:limit]


def format_recommendations(recommendations: Iterable[dict[str, object]]) -> str:
    """Format recommendations for CLI output."""

    lines = []
    for issue in recommendations:
        stack = ", ".join(issue["stack"])
        lines.append(
            f"{issue['id']} | score {issue['score']} | {issue['area']} | "
            f"{issue['effort']} | {stack}\n  {issue['description']}"
        )
    return "\n".join(lines)


def _feedback_score(issue: IssueCandidate, feedback_items: Iterable[dict[str, object]]) -> int:
    score = 0
    issue_stack = set(issue.stack)
    for item in feedback_items:
        issue_id = item.get("issue_id")
        liked = bool(item.get("liked", True))
        if not issue_id:
            continue
        reference = get_issue_by_id(str(issue_id))
        direction = 1 if liked else -1
        if issue.id == reference.id:
            score += direction * 5
        if issue.area == reference.area:
            score += direction * 3
        if issue.effort == reference.effort:
            score += direction
        score += direction * len(issue_stack.intersection(reference.stack))
    return score


def _validate_option(name: str, value: str, options: dict[str, list[int]]) -> None:
    if value not in options:
        valid = ", ".join(sorted(options))
        raise ValueError(f"Unknown {name}: {value}. Expected one of: {valid}")
