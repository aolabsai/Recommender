"""CLI and Streamlit demo for the open-source issue recommender domain."""

from __future__ import annotations

import argparse

from open_source_issue_domain import format_recommendations, rank_issues


def recommend(
    preferred_area: str = "any",
    effort_budget: str = "medium",
    contributor_level: str = "intermediate",
    wants_beginner_friendly: bool = False,
    goal: str = "quick-win",
    stack: list[str] | None = None,
    feedback: list[dict[str, object]] | None = None,
    limit: int = 5,
) -> list[dict[str, object]]:
    """Return ranked open-source issues through the deterministic fallback recommender."""

    return rank_issues(
        preferred_area=preferred_area,
        effort_budget=effort_budget,
        contributor_level=contributor_level,
        wants_beginner_friendly=wants_beginner_friendly,
        goal=goal,
        stack=stack,
        feedback=feedback,
        limit=limit,
    )


def run_cli(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Recommend open-source issues for a contributor profile.")
    parser.add_argument(
        "--area",
        default="any",
        choices=["any", "frontend", "backend", "docs", "testing", "devops", "data", "cli"],
    )
    parser.add_argument("--effort", default="medium", choices=["small", "medium", "large"])
    parser.add_argument("--level", default="intermediate", choices=["new", "intermediate", "experienced"])
    parser.add_argument("--beginner-friendly", action="store_true")
    parser.add_argument(
        "--goal",
        default="quick-win",
        choices=["learn", "quick-win", "portfolio", "maintainer-impact"],
    )
    parser.add_argument("--stack", action="append", default=[])
    parser.add_argument("--liked-issue", action="append", default=[])
    parser.add_argument("--disliked-issue", action="append", default=[])
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    feedback = [{"issue_id": issue_id, "liked": True} for issue_id in args.liked_issue]
    feedback.extend({"issue_id": issue_id, "liked": False} for issue_id in args.disliked_issue)

    recommendations = recommend(
        preferred_area=args.area,
        effort_budget=args.effort,
        contributor_level=args.level,
        wants_beginner_friendly=args.beginner_friendly,
        goal=args.goal,
        stack=args.stack,
        feedback=feedback,
        limit=args.limit,
    )
    print(format_recommendations(recommendations))


def run_streamlit() -> None:
    import streamlit as st

    st.title("Open-Source Issue Recommender")
    st.caption("An offline AO-compatible domain for matching contributors with issue profiles.")

    preferred_area = st.selectbox(
        "Preferred area",
        ["any", "frontend", "backend", "docs", "testing", "devops", "data", "cli"],
    )
    effort_budget = st.radio("Effort budget", ["small", "medium", "large"], index=1, horizontal=True)
    contributor_level = st.radio(
        "Contributor level",
        ["new", "intermediate", "experienced"],
        index=1,
        horizontal=True,
    )
    wants_beginner_friendly = st.checkbox("Prefer beginner-friendly issues")
    goal = st.selectbox("Contribution goal", ["learn", "quick-win", "portfolio", "maintainer-impact"])
    stack = st.multiselect(
        "Known stack",
        [
            "accessibility",
            "api",
            "bash",
            "benchmark",
            "ci",
            "css",
            "csv",
            "database",
            "docker",
            "docs",
            "github-actions",
            "mdx",
            "node",
            "python",
            "react",
            "storybook",
            "typescript",
        ],
    )
    liked_issues = st.multiselect(
        "Recommend more like",
        [
            "keyboard-navigation-audit",
            "flaky-date-parser-test",
            "api-pagination-bounds",
            "docker-healthcheck",
            "docs-install-paths",
            "csv-import-memory",
            "cli-config-precedence",
            "storybook-empty-state",
            "scheduler-race-condition",
            "ci-cache-split",
            "benchmark-data-fixture",
            "upgrade-guide-mdx",
        ],
    )

    feedback = [{"issue_id": issue_id, "liked": True} for issue_id in liked_issues]
    recommendations = recommend(
        preferred_area=preferred_area,
        effort_budget=effort_budget,
        contributor_level=contributor_level,
        wants_beginner_friendly=wants_beginner_friendly,
        goal=goal,
        stack=stack,
        feedback=feedback,
    )

    for issue in recommendations:
        st.subheader(f"{issue['title']} - score {issue['score']}")
        st.write(issue["description"])
        st.write("Area:", issue["area"], "| Effort:", issue["effort"], "| Risk:", issue["risk"])
        st.write("AO input:", issue["binary_input"])
        st.write("Stack:", ", ".join(issue["stack"]))


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False
    return get_script_run_ctx() is not None


if __name__ == "__main__":
    if _running_in_streamlit():
        run_streamlit()
    else:
        run_cli()
