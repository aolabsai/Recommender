"""Streamlit demo and CLI fallback for the volunteering recommender domain."""

from __future__ import annotations

import argparse
from collections import defaultdict

from volunteer_domain import (
    GOAL_BITS,
    TIME_BITS,
    VOLUNTEER_CATALOG,
    encode_opportunity,
    recommend_opportunities,
)


def _try_create_agent():
    try:
        import ao_core as ao
        from arch__VolunteerRecommender import arch
    except Exception:
        return None
    return ao.Agent(arch, notes="Volunteer Recommender")


def _agent_score(agent, binary_input: list[int]) -> int:
    if agent is None:
        return 0
    agent.reset_state()
    response = agent.next_state(INPUT=binary_input, print_result=False)
    return sum(int(bit) for bit in response)


def run_cli(args: argparse.Namespace) -> None:
    feedback = defaultdict(int)
    if args.prefer_category:
        feedback[args.prefer_category] += 2

    agent = _try_create_agent()
    recommendations = recommend_opportunities(
        args.goal,
        max_time=args.max_time,
        skilled_ok=args.skilled_ok,
        feedback=dict(feedback),
        limit=args.limit,
    )

    for opportunity in recommendations:
        binary_input = encode_opportunity(opportunity, args.goal)
        ao_score = _agent_score(agent, binary_input)
        print(f"- {opportunity.name}")
        print(f"  category: {opportunity.category}")
        print(f"  time: {opportunity.time_commitment}")
        print(f"  skill: {opportunity.skill_level}")
        print(f"  setting: {opportunity.setting}")
        print(f"  encoded_input: {binary_input}")
        if agent is not None:
            print(f"  ao_score: {ao_score}")
        print(f"  why: {opportunity.description}")


def run_streamlit() -> None:
    import streamlit as st

    st.set_page_config(page_title="Volunteer Recommender", layout="wide")
    st.title("Community Volunteering Recommender")

    goal = st.selectbox("Goal", tuple(GOAL_BITS.keys()), format_func=lambda x: x.replace("_", " ").title())
    max_time = st.selectbox(
        "Maximum time commitment",
        tuple(TIME_BITS.keys()),
        index=3,
        format_func=lambda x: x.replace("_", " ").title(),
    )
    skilled_ok = st.checkbox("Include skilled opportunities", value=True)

    feedback = defaultdict(int)
    liked = st.multiselect(
        "Categories to recommend more often",
        sorted({item.category for item in VOLUNTEER_CATALOG}),
        format_func=lambda x: x.replace("_", " ").title(),
    )
    for category in liked:
        feedback[category] += 2

    agent = _try_create_agent()
    if agent is None:
        st.info("Running deterministic fallback mode. Install ao_core and ao_arch to enable live AO scoring.")

    for opportunity in recommend_opportunities(goal, max_time, skilled_ok, dict(feedback), limit=5):
        binary_input = encode_opportunity(opportunity, goal)
        ao_score = _agent_score(agent, binary_input)
        with st.container(border=True):
            st.subheader(opportunity.name)
            st.write(opportunity.description)
            st.write(
                {
                    "category": opportunity.category,
                    "time_commitment": opportunity.time_commitment,
                    "skill_level": opportunity.skill_level,
                    "setting": opportunity.setting,
                    "impact": opportunity.impact,
                    "encoded_input": binary_input,
                }
            )
            if agent is not None:
                st.write(f"AO score: {ao_score}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recommend volunteering opportunities.")
    parser.add_argument("--goal", choices=tuple(GOAL_BITS.keys()), default="high_impact")
    parser.add_argument("--max-time", choices=tuple(TIME_BITS.keys()), default="ongoing")
    parser.add_argument("--prefer-category", default=None)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--skilled-ok", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    try:
        import streamlit.runtime.scriptrunner as scriptrunner
    except Exception:
        scriptrunner = None

    if scriptrunner is not None and scriptrunner.get_script_run_ctx() is not None:
        run_streamlit()
    else:
        run_cli(parse_args())

