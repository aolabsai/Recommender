"""Streamlit and CLI demo for a plant care recommender domain."""

from __future__ import annotations

from plant_domain import (
    PLANT_ACTIONS,
    apply_feedback,
    encode_plant_action,
    recommend_plant_actions,
)


def create_agent():
    """Create an AO Agent when optional AO packages are installed."""

    try:
        import ao_core as ao
        from arch__PlantRecommender import arch
    except Exception:
        return None

    agent = ao.Agent(arch, notes="Plant Care Agent")
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

    print("Top plant care recommendations:")
    for action, score in recommend_plant_actions(goal="easy-care", minutes_available=15):
        print(f"- {action.name} ({score})")
        print(f"  input={encode_plant_action(action, 'easy-care')}")
        print(f"  {action.description}")


def run_streamlit() -> None:
    """Run the interactive Streamlit demo."""

    import streamlit as st

    st.set_page_config(
        page_title="Plant Care Recommender by AO Labs",
        page_icon="misc/ao_favicon.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    if "plant_feedback" not in st.session_state:
        st.session_state.plant_feedback = {}
    if "plant_agent" not in st.session_state:
        st.session_state.plant_agent = create_agent()

    st.title("Plant Care Recommender")
    st.write("A domain adaptation of the AO recommender for indoor plant care actions.")

    with st.sidebar:
        goal = st.selectbox(
            "Care goal",
            ("easy-care", "faster-growth", "fix-symptoms", "harvest"),
            index=0,
            format_func=lambda value: value.replace("-", " ").title(),
        )
        indoor_light = st.selectbox(
            "Available light",
            ("low", "medium", "bright"),
            index=1,
            format_func=str.title,
        )
        minutes_available = st.slider("Minutes available today", 5, 45, 15, 5)
        ao_status = "available" if st.session_state.plant_agent is not None else "fallback mode"
        st.write(f"AO Agent: {ao_status}")

    ranked = recommend_plant_actions(
        goal=goal,
        minutes_available=minutes_available,
        indoor_light=indoor_light,
        feedback=st.session_state.plant_feedback,
        limit=len(PLANT_ACTIONS),
    )

    for action, fallback_score in ranked[:5]:
        binary_input = encode_plant_action(action, goal)
        ao_score = ao_percentage(st.session_state.plant_agent, binary_input)
        display_score = ao_score if ao_score is not None else fallback_score

        st.subheader(action.name)
        st.write(action.description)
        st.write(
            {
                "plant_type": action.plant_type,
                "light": action.light,
                "effort": action.effort,
                "water_need": action.water_need,
                "minutes": action.minutes,
                "encoded_input": binary_input,
                "score": display_score,
            }
        )

        left, right = st.columns(2)
        if left.button("Recommend more like this", key=f"like-{action.name}"):
            st.session_state.plant_feedback = apply_feedback(
                st.session_state.plant_feedback, action.name, liked=True
            )
            train_agent(st.session_state.plant_agent, binary_input, liked=True)
            st.rerun()
        if right.button("Recommend less like this", key=f"less-{action.name}"):
            st.session_state.plant_feedback = apply_feedback(
                st.session_state.plant_feedback, action.name, liked=False
            )
            train_agent(st.session_state.plant_agent, binary_input, liked=False)
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
