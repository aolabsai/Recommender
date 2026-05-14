"""Streamlit and CLI demo for a wellness micro-habit recommender domain."""

from __future__ import annotations

from wellness_domain import (
    WELLNESS_HABITS,
    apply_feedback,
    encode_wellness_habit,
    recommend_wellness_habits,
)


def create_agent():
    """Create an AO Agent when optional AO packages are installed."""

    try:
        import ao_core as ao
        from arch__WellnessRecommender import arch
    except Exception:
        return None

    agent = ao.Agent(arch, notes="Wellness Micro-Habit Agent")
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

    print("Top wellness micro-habit recommendations:")
    for habit, score in recommend_wellness_habits(goal="calm", minutes_available=15):
        print(f"- {habit.name} ({score})")
        print(f"  input={encode_wellness_habit(habit, 'calm')}")
        print(f"  {habit.description}")


def run_streamlit() -> None:
    """Run the interactive Streamlit demo."""

    import streamlit as st

    st.set_page_config(
        page_title="Wellness Recommender by AO Labs",
        page_icon="misc/ao_favicon.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "wellness_feedback" not in st.session_state:
        st.session_state.wellness_feedback = {}
    if "wellness_agent" not in st.session_state:
        st.session_state.wellness_agent = create_agent()

    st.title("Wellness Micro-Habit Recommender")
    st.write("A domain adaptation of the AO recommender for everyday wellness habits.")

    with st.sidebar:
        goal = st.selectbox(
            "Current goal",
            ("calm", "better-sleep", "deep-work", "reset"),
            index=0,
            format_func=lambda value: value.replace("-", " ").title(),
        )
        preferred_energy = st.selectbox(
            "Preferred effort level",
            ("low", "medium"),
            index=0,
            format_func=str.title,
        )
        minutes_available = st.slider("Minutes available", 2, 40, 15, 1)
        social_ok = st.checkbox("Include social habits", value=True)
        ao_status = "available" if st.session_state.wellness_agent is not None else "fallback mode"
        st.write(f"AO Agent: {ao_status}")

    ranked = recommend_wellness_habits(
        goal=goal,
        minutes_available=minutes_available,
        preferred_energy=preferred_energy,
        social_ok=social_ok,
        feedback=st.session_state.wellness_feedback,
        limit=len(WELLNESS_HABITS),
    )

    for habit, fallback_score in ranked[:5]:
        binary_input = encode_wellness_habit(habit, goal)
        ao_score = ao_percentage(st.session_state.wellness_agent, binary_input)
        display_score = ao_score if ao_score is not None else fallback_score

        st.subheader(habit.name)
        st.write(habit.description)
        st.write(
            {
                "focus": habit.focus,
                "time_bucket": habit.time_bucket,
                "social": habit.social,
                "energy_level": habit.energy_level,
                "minutes": habit.minutes,
                "encoded_input": binary_input,
                "score": display_score,
            }
        )

        left, right = st.columns(2)
        if left.button("Recommend more like this", key=f"like-{habit.name}"):
            st.session_state.wellness_feedback = apply_feedback(
                st.session_state.wellness_feedback, habit.name, liked=True
            )
            train_agent(st.session_state.wellness_agent, binary_input, liked=True)
            st.rerun()
        if right.button("Recommend less like this", key=f"less-{habit.name}"):
            st.session_state.wellness_feedback = apply_feedback(
                st.session_state.wellness_feedback, habit.name, liked=False
            )
            train_agent(st.session_state.wellness_agent, binary_input, liked=False)
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
