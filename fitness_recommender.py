"""Streamlit demo for a continuously trainable workout recommender.

The app runs with a deterministic fallback recommender by default. If AO Labs'
private packages are installed, it can also instantiate an AO Agent using
``arch__FitnessRecommender.py`` and show the binary input sent to the agent.
"""

from __future__ import annotations

import numpy as np
import streamlit as st

from fitness_domain import (
    ENERGY_LEVELS,
    EQUIPMENT,
    GOALS,
    INPUT_SCHEMA,
    normalize_context,
    recommend_workouts,
)


def maybe_create_agent():
    try:
        import ao_core as ao
        from arch__FitnessRecommender import arch
    except Exception:
        return None
    return ao.Agent(arch, notes="Fitness Workout Agent")


def summarize_bits(bits: list[int]) -> str:
    cursor = 0
    parts = []
    for name, width in INPUT_SCHEMA:
        segment = bits[cursor : cursor + width]
        parts.append(f"{name}={''.join(str(bit) for bit in segment)}")
        cursor += width
    return " | ".join(parts)


st.set_page_config(
    page_title="AO Labs Fitness Recommender",
    page_icon="misc/ao_favicon.png",
    layout="wide",
)

if "fitness_agent" not in st.session_state:
    st.session_state.fitness_agent = maybe_create_agent()
if "fitness_feedback" not in st.session_state:
    st.session_state.fitness_feedback = []

st.title("Continuously Trainable Fitness Recommender")
st.write(
    "A domain adaptation of the AO Labs recommender for workout selection. "
    "It maps workout metadata plus user context into binary inputs, then ranks "
    "workouts with a deterministic fallback when AO packages are unavailable."
)

with st.sidebar:
    st.header("User Context")
    goal = st.selectbox("Training goal", GOALS, index=0)
    energy = st.selectbox("Current energy", ENERGY_LEVELS, index=1)
    equipment = st.selectbox("Available equipment", EQUIPMENT, index=0)
    time_budget_min = st.slider("Time budget", min_value=5, max_value=60, value=30, step=5)
    st.divider()
    if st.session_state.fitness_agent is None:
        st.info("AO packages not installed; using deterministic fallback ranking.")
    else:
        st.success("AO Agent loaded.")

context = normalize_context(
    {
        "goal": goal,
        "energy": energy,
        "equipment": equipment,
        "time_budget_min": time_budget_min,
    }
)

recommendations = recommend_workouts(context, limit=5)

for rank, (workout, score, bits) in enumerate(recommendations, start=1):
    with st.container(border=True):
        left, right = st.columns([0.74, 0.26])
        with left:
            st.subheader(f"{rank}. {workout.title}")
            st.write(workout.description)
            st.caption(
                f"{workout.goal.title()} | {workout.intensity.title()} intensity | "
                f"{workout.duration_min} min | Equipment: {workout.equipment}"
            )
            st.code(summarize_bits(bits), language="text")
        with right:
            st.metric("Fallback score", score)
            if st.button("Recommend more", key=f"more-{workout.id}"):
                st.session_state.fitness_feedback.append((workout.id, "more"))
                if st.session_state.fitness_agent is not None:
                    label = np.ones(st.session_state.fitness_agent.arch.Z__flat.shape, dtype=np.int8)
                    st.session_state.fitness_agent.next_state(
                        INPUT=bits,
                        LABEL=label,
                        print_result=False,
                        unsequenced=True,
                    )
            if st.button("Recommend less", key=f"less-{workout.id}"):
                st.session_state.fitness_feedback.append((workout.id, "less"))
                if st.session_state.fitness_agent is not None:
                    label = np.zeros(st.session_state.fitness_agent.arch.Z__flat.shape, dtype=np.int8)
                    st.session_state.fitness_agent.next_state(
                        INPUT=bits,
                        LABEL=label,
                        print_result=False,
                        unsequenced=True,
                    )

if st.session_state.fitness_feedback:
    st.divider()
    st.write("Feedback captured this session:")
    st.dataframe(
        [{"workout_id": workout_id, "feedback": feedback} for workout_id, feedback in st.session_state.fitness_feedback],
        use_container_width=True,
    )

