from dataclasses import dataclass
from typing import Iterable


TRACK_BITS = {
    "bug": [0, 0, 0],
    "docs": [0, 0, 1],
    "tests": [0, 1, 0],
    "security": [0, 1, 1],
    "performance": [1, 0, 0],
    "frontend": [1, 0, 1],
    "backend": [1, 1, 0],
    "automation": [1, 1, 1],
}

DIFFICULTY_BITS = {
    "beginner": [0, 0],
    "intermediate": [0, 1],
    "advanced": [1, 0],
    "expert": [1, 1],
}

GOAL_BITS = {
    "learn": [0, 0],
    "quick-win": [0, 1],
    "portfolio": [1, 0],
    "maintainer": [1, 1],
}


@dataclass(frozen=True)
class IssueTask:
    title: str
    project: str
    track: str
    difficulty: str
    minutes: int
    impact: int
    tags: tuple[str, ...]
    summary: str


ISSUE_CATALOG = [
    IssueTask(
        title="Add regression tests for retry backoff jitter",
        project="Async API client",
        track="tests",
        difficulty="intermediate",
        minutes=45,
        impact=7,
        tags=("python", "tests", "networking"),
        summary="Cover retry delays and max-attempt behavior without hitting the network.",
    ),
    IssueTask(
        title="Document OAuth token rotation failure modes",
        project="Identity gateway",
        track="docs",
        difficulty="beginner",
        minutes=35,
        impact=5,
        tags=("docs", "security", "oauth"),
        summary="Turn scattered maintainer notes into a troubleshooting guide.",
    ),
    IssueTask(
        title="Fix stale cache invalidation after workspace rename",
        project="Developer dashboard",
        track="frontend",
        difficulty="intermediate",
        minutes=70,
        impact=8,
        tags=("react", "state", "cache"),
        summary="Refresh workspace-scoped queries after a rename mutation succeeds.",
    ),
    IssueTask(
        title="Harden archive extraction against path traversal",
        project="Release packager",
        track="security",
        difficulty="advanced",
        minutes=95,
        impact=10,
        tags=("security", "filesystem", "python"),
        summary="Reject archive entries that escape the intended extraction directory.",
    ),
    IssueTask(
        title="Speed up dependency graph rendering",
        project="Build visualizer",
        track="performance",
        difficulty="advanced",
        minutes=120,
        impact=9,
        tags=("typescript", "performance", "graphs"),
        summary="Memoize layout inputs and virtualize large dependency lists.",
    ),
    IssueTask(
        title="Add CLI smoke test to release workflow",
        project="Command runner",
        track="automation",
        difficulty="beginner",
        minutes=30,
        impact=6,
        tags=("github-actions", "cli", "tests"),
        summary="Run the packaged binary with --help before publishing releases.",
    ),
    IssueTask(
        title="Normalize webhook signature errors",
        project="Billing backend",
        track="backend",
        difficulty="intermediate",
        minutes=60,
        impact=8,
        tags=("api", "webhooks", "payments"),
        summary="Return consistent 400 responses for malformed signature headers.",
    ),
    IssueTask(
        title="Improve empty-state copy for filtered search",
        project="Knowledge base",
        track="frontend",
        difficulty="beginner",
        minutes=25,
        impact=4,
        tags=("ux", "search", "copy"),
        summary="Make the no-results state explain active filters and reset actions.",
    ),
    IssueTask(
        title="Add contract tests for pagination cursors",
        project="Data export API",
        track="tests",
        difficulty="advanced",
        minutes=110,
        impact=9,
        tags=("api", "tests", "pagination"),
        summary="Verify stable forward/backward pagination across deleted records.",
    ),
    IssueTask(
        title="Replace shell-built cleanup paths with pathlib checks",
        project="Local dev installer",
        track="security",
        difficulty="intermediate",
        minutes=55,
        impact=8,
        tags=("python", "security", "installer"),
        summary="Resolve and validate cleanup targets before deleting generated files.",
    ),
    IssueTask(
        title="Add first-run examples to configuration docs",
        project="Telemetry collector",
        track="docs",
        difficulty="beginner",
        minutes=40,
        impact=5,
        tags=("docs", "observability", "yaml"),
        summary="Show minimal configs for local files, HTTP input, and stdout export.",
    ),
    IssueTask(
        title="Batch database lookups in notification fan-out",
        project="Messaging service",
        track="backend",
        difficulty="expert",
        minutes=150,
        impact=10,
        tags=("database", "performance", "notifications"),
        summary="Replace per-recipient preference queries with one batched lookup.",
    ),
]


def encode_issue(issue: IssueTask, goal: str) -> list[int]:
    if issue.track not in TRACK_BITS:
        raise ValueError(f"Unsupported track: {issue.track}")
    if issue.difficulty not in DIFFICULTY_BITS:
        raise ValueError(f"Unsupported difficulty: {issue.difficulty}")
    if goal not in GOAL_BITS:
        raise ValueError(f"Unsupported goal: {goal}")

    short_task = 0 if issue.minutes <= 60 else 1
    return TRACK_BITS[issue.track] + DIFFICULTY_BITS[issue.difficulty] + [short_task] + GOAL_BITS[goal]


def score_issue(issue: IssueTask, preferred_tracks: Iterable[str], goal: str, max_minutes: int) -> float:
    preferred_tracks = set(preferred_tracks)
    score = issue.impact * 10

    if issue.track in preferred_tracks:
        score += 25
    if issue.minutes <= max_minutes:
        score += 20
    else:
        score -= min(35, (issue.minutes - max_minutes) / 3)

    if goal == "quick-win":
        score += 18 if issue.minutes <= 45 else -10
        score += 8 if issue.difficulty == "beginner" else 0
    elif goal == "learn":
        score += 12 if issue.difficulty in {"beginner", "intermediate"} else 0
    elif goal == "portfolio":
        score += 15 if issue.impact >= 8 else 0
        score += 8 if issue.difficulty in {"intermediate", "advanced"} else 0
    elif goal == "maintainer":
        score += 15 if issue.track in {"tests", "security", "automation"} else 0
        score += 10 if issue.impact >= 7 else 0

    return round(score, 2)


def recommend_issues(preferred_tracks: Iterable[str], goal: str, max_minutes: int, limit: int = 5) -> list[dict]:
    ranked = []
    for issue in ISSUE_CATALOG:
        ranked.append(
            {
                "issue": issue,
                "encoding": encode_issue(issue, goal),
                "score": score_issue(issue, preferred_tracks, goal, max_minutes),
            }
        )
    return sorted(ranked, key=lambda item: item["score"], reverse=True)[:limit]
