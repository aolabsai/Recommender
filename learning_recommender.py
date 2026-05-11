from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from learning_domain import (
    LEARNING_CATALOG,
    encode_learning_resource,
    format_learning_card,
    pick_next_learning_resource,
    recommendation_percentage,
)

try:
    import ao_core as ao
    from arch__LearningRecommender import arch
except ImportError:
    ao = None
    arch = None


LEARNING_GOALS = (
    "Surprise me",
    "Ship a prototype",
    "Deepen fundamentals",
    "Prepare for interview",
)


def ensure_state() -> None:
    st.session_state.setdefault("seen_learning_titles", [])
    st.session_state.setdefault("learning_index_seed", 0)
    st.session_state.setdefault("learning_feedback_history", [])
    st.session_state.setdefault("current_learning_bits", [])
    st.session_state.setdefault(
        "current_learning_resource",
        pick_next_learning_resource([], 0),
    )

    if "learning_agent" not in st.session_state and ao is not None:
        st.session_state.learning_agent = ao.Agent(
            arch,
            notes="Learning Resource Domain Agent",
        )
        for _ in range(4):
            st.session_state.learning_agent.reset_state()
            st.session_state.learning_agent.reset_state(training=True)


def fallback_response(binary_input: list[int]) -> list[int]:
    score = sum(binary_input)
    return [1 if (score + idx) % 4 != 0 else 0 for idx in range(10)]


def agent_response(binary_input: list[int]) -> list[int]:
    if ao is None:
        return fallback_response(binary_input)

    st.session_state.learning_agent.reset_state()
    response = None
    for _ in range(5):
        response = st.session_state.learning_agent.next_state(
            INPUT=binary_input,
            print_result=False,
        )
    return response


def train_agent(user_response: str) -> None:
    if ao is None:
        return

    label_value = 1 if user_response == "Recommend more" else 0
    label = np.full(
        st.session_state.learning_agent.arch.Z__flat.shape,
        label_value,
        dtype=np.int8,
    )
    repetitions = 6 if label_value else 10

    for _ in range(repetitions):
        st.session_state.learning_agent.reset_state()
        st.session_state.learning_agent.next_state(
            INPUT=st.session_state.current_learning_bits,
            LABEL=label,
            print_result=False,
            unsequenced=True,
        )


def advance_resource() -> None:
    st.session_state.seen_learning_titles.append(
        st.session_state.current_learning_resource.title
    )
    st.session_state.learning_index_seed += 1
    st.session_state.current_learning_resource = pick_next_learning_resource(
        st.session_state.seen_learning_titles,
        st.session_state.learning_index_seed,
    )


st.set_page_config(
    page_title="Learning Recommender Demo by AO Labs",
    page_icon="misc/ao_favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_state()

with st.sidebar:
    st.write("## Learning Dataset")
    st.write(f"{len(LEARNING_CATALOG)} sample resources")
    st.write(
        "This demo maps local learning resources into binary features for topic, "
        "format, duration, difficulty, hands-on style, free/paid status, and learner goal."
    )
    if ao is None:
        st.warning(
            "AO packages are not installed, so the app is using a deterministic local "
            "response. Install ao_core and ao_arch to train a live AO Agent."
        )
    elif st.button("Reset Learning Agent"):
        del st.session_state.learning_agent
        ensure_state()
        st.success("Learning Agent reset")

st.title("Real-Time Personal Learning Resource Recommender")
st.write(
    "A learning-domain demo for AO Labs' continuously trainable recommender."
)

goal = st.selectbox("Set your current learning goal:", LEARNING_GOALS)
resource = st.session_state.current_learning_resource
binary_input = encode_learning_resource(resource, goal)
st.session_state.current_learning_bits = binary_input

response = agent_response(binary_input)
recommendation = recommendation_percentage(response)

left, right = st.columns([0.6, 0.4], gap="large")

with left:
    st.markdown(format_learning_card(resource))
    st.write(f"Agent recommendation: {recommendation}%")
    st.progress(recommendation)
    st.caption(f"Agent input bits: {binary_input}")

with right:
    if st.button("Recommend more", type="primary"):
        train_agent("Recommend more")
        st.session_state.learning_feedback_history.append(
            [resource.title, goal, recommendation, "Recommend more"]
        )
        advance_resource()
        st.rerun()

    if st.button("Stop recommending"):
        train_agent("Stop recommending")
        st.session_state.learning_feedback_history.append(
            [resource.title, goal, recommendation, "Stop recommending"]
        )
        advance_resource()
        st.rerun()

    if st.button("Skip"):
        st.session_state.learning_feedback_history.append(
            [resource.title, goal, recommendation, "Skipped"]
        )
        advance_resource()
        st.rerun()

st.write("---")
st.write("### Training History")

if st.session_state.learning_feedback_history:
    st.dataframe(
        pd.DataFrame(
            st.session_state.learning_feedback_history,
            columns=["Resource", "Goal", "Recommendation", "Feedback"],
        ),
        use_container_width=True,
    )
else:
    st.info("Rate a resource to start training this learning-domain agent.")
