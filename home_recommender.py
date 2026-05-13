"""Streamlit and CLI demo for a home maintenance recommender domain."""

from __future__ import annotations

from home_domain import (
    HOME_TASKS,
    apply_feedback,
    encode_home_task,
    recommend_home_tasks,
)


def create_agent():
    """Create an AO Agent when optional AO packages are installed."""

    try:
        import ao_core as ao
        from arch__HomeRecommender import arch
    except Exception:
        return None

    agent = ao.Agent(arch, notes="Home Maintenance Agent")
    for _ in range(4):
        agent.reset_state()
        agent.reset_state(training=True)
    return agent


def ao_percentage(agent, binary_input: list[int]) -> int | None:
    """Return an AO recommendation percentage, or None when AO is unavailable."""

    if agent is None:
        return None

    agent.reset_state()
    response = None
    for _ in range(5):
        response = agent.next_state(INPUT=binary_input, print_result=False)

    if response is None:
        return None

    return round(sum(1 for value in response if value == 1) / len(response) * 100)


def train_agent(agent, binary_input: list[int], liked: bool) -> None:
    """Train the optional AO Agent on user feedback."""

    if agent is None:
        return

    import numpy as np

    label_value = 1 if liked else 0
    label = np.full(agent.arch.Z__flat.shape, label_value, dtype=np.int8)
    for _ in range(5 if liked else 10):
        agent.reset_state()
        agent.next_state(INPUT=binary_input, LABEL=label, print_result=False, unsequenced=True)


def run_cli() -> None:
    """Print fallback recommendations without requiring Streamlit or AO packages."""

    print("Top home maintenance recommendations:")
    for task, score in recommend_home_tasks(goal="prevent-breakdowns", minutes_available=45):
        print(f"- {task.name} ({score})")
        print(f"  input={encode_home_task(task, 'prevent-breakdowns')}")
        print(f"  {task.description}")


def run_streamlit() -> None:
    """Run the interactive Streamlit demo."""

    import streamlit as st

    st.set_page_config(
        page_title="Home Maintenance Recommender by AO Labs",
        page_icon="misc/ao_favicon.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "home_feedback" not in st.session_state:
        st.session_state.home_feedback = {}
    if "home_agent" not in st.session_state:
        st.session_state.home_agent = create_agent()

    st.title("Home Maintenance Recommender")
    st.write("A domain adaptation of the AO recommender for household upkeep and repair prevention.")

    with st.sidebar:
        goal = st.selectbox(
            "Household goal",
            ("safety", "save-money", "prevent-breakdowns", "clean-comfort"),
            index=2,
            format_func=lambda value: value.replace("-", " ").title(),
        )
        minutes_available = st.slider("Minutes available today", 10, 120, 45, 5)
        prefer_low_cost = st.checkbox("Prefer free or low-cost tasks", value=True)
        ao_status = "available" if st.session_state.home_agent is not None else "fallback mode"
        st.write(f"AO Agent: {ao_status}")

    ranked = recommend_home_tasks(
        goal=goal,
        minutes_available=minutes_available,
        prefer_low_cost=prefer_low_cost,
        feedback=st.session_state.home_feedback,
        limit=len(HOME_TASKS),
    )

    for task, fallback_score in ranked[:5]:
        binary_input = encode_home_task(task, goal)
        ao_score = ao_percentage(st.session_state.home_agent, binary_input)
        display_score = ao_score if ao_score is not None else fallback_score

        st.subheader(task.name)
        st.write(task.description)
        st.write(
            {
                "category": task.category,
                "urgency": task.urgency,
                "effort": task.effort,
                "cost_tier": task.cost_tier,
                "minutes": task.minutes,
                "encoded_input": binary_input,
                "score": display_score,
            }
        )

        left, right = st.columns(2)
        if left.button("Recommend more like this", key=f"like-{task.name}"):
            st.session_state.home_feedback = apply_feedback(
                st.session_state.home_feedback, task.name, liked=True
            )
            train_agent(st.session_state.home_agent, binary_input, liked=True)
            st.rerun()
        if right.button("Recommend less like this", key=f"less-{task.name}"):
            st.session_state.home_feedback = apply_feedback(
                st.session_state.home_feedback, task.name, liked=False
            )
            train_agent(st.session_state.home_agent, binary_input, liked=False)
            st.rerun()


def is_streamlit_runtime() -> bool:
    """Detect whether this script is being executed by Streamlit."""

    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False

    return get_script_run_ctx() is not None


if __name__ == "__main__":
    if is_streamlit_runtime():
        run_streamlit()
    else:
        run_cli()
