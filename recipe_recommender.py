from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from recipe_domain import (
    DIETARY_FLAGS,
    MEAL_SLOTS,
    MOODS,
    MealContext,
    feedback_label,
    recommend_recipes,
)

try:
    import ao_core as ao
    from arch__RecipeRecommender import arch
except ImportError:
    ao = None
    arch = None


def _ensure_state() -> None:
    if "recipe_agent" not in st.session_state:
        if ao and arch:
            st.session_state.recipe_agent = ao.Agent(arch, notes="Recipe Agent")
            for _ in range(4):
                st.session_state.recipe_agent.reset_state()
                st.session_state.recipe_agent.reset_state(training=True)
        else:
            st.session_state.recipe_agent = None
    if "last_recipe_input" not in st.session_state:
        st.session_state.last_recipe_input = None


def _agent_percentage(binary_input: list[int], fallback_score: int) -> int:
    agent = st.session_state.recipe_agent
    if agent is None:
        return fallback_score
    agent.reset_state()
    response = None
    for _ in range(5):
        response = agent.next_state(INPUT=binary_input, print_result=False)
    return round((sum(response) / len(response)) * 100)


def _train_agent(liked: bool) -> None:
    agent = st.session_state.recipe_agent
    binary_input = st.session_state.last_recipe_input
    if agent is None or binary_input is None:
        return
    label = np.array(feedback_label(liked, agent.arch.Z__flat.shape[0]), dtype=np.int8)
    for _ in range(6 if liked else 10):
        agent.reset_state()
        agent.next_state(INPUT=binary_input, LABEL=label, print_result=False, unsequenced=True)


st.set_page_config(
    page_title="Recipe Recommender Demo by AO Labs",
    page_icon="misc/ao_favicon.png",
    layout="wide",
)

_ensure_state()

st.title("Real-Time Recipe Recommender")
st.write(
    "### A new recipe and meal-planning domain for AO Labs' continuously trainable "
    "recommender"
)

with st.sidebar:
    st.write("## Meal Context")
    meal_slot = st.selectbox("Meal", MEAL_SLOTS, index=MEAL_SLOTS.index("dinner"))
    mood = st.selectbox("Mood", MOODS, index=MOODS.index("balanced"))
    max_cook_time = st.slider(
        "Max cook time",
        min_value=10,
        max_value=75,
        value=35,
        step=5,
    )
    dietary_options = ("none",) + DIETARY_FLAGS
    dietary_choice = st.selectbox("Dietary preference", dietary_options)
    dietary_preference = None if dietary_choice == "none" else dietary_choice

    st.write("---")
    if st.session_state.recipe_agent is None:
        st.info(
            "AO packages are not installed, so this demo is using the deterministic "
            "fallback scorer."
        )
    else:
        st.success("Live AO Agent loaded.")

    if st.button("Recommend More Like Last Recipe", type="primary"):
        _train_agent(True)
    if st.button("Less Like Last Recipe"):
        _train_agent(False)

context = MealContext(
    meal_slot=meal_slot,
    mood=mood,
    max_cook_time_minutes=max_cook_time,
    dietary_preference=dietary_preference,
)

recommendations = recommend_recipes(context, limit=5)

for rank, (recipe, fallback_score, binary_input) in enumerate(recommendations, start=1):
    if rank == 1:
        st.session_state.last_recipe_input = binary_input
    agent_score = _agent_percentage(binary_input, fallback_score)
    with st.container(border=True):
        st.subheader(f"{rank}. {recipe.title}")
        st.write(recipe.description)
        st.write(
            f"**Cuisine:** {recipe.cuisine} | **Meal:** {recipe.meal_slot} | "
            f"**Time:** {recipe.cook_time_minutes} min | **Difficulty:** {recipe.difficulty}"
        )
        st.write("**Tags:** " + ", ".join(recipe.dietary_tags))
        st.progress(agent_score / 100, text=f"Recommendation strength: {agent_score}%")

st.write("---")
st.write("### Feature Encoding")
encoding_rows = [
    {
        "recipe": recipe.title,
        "fallback_score": score,
        "binary_input": "".join(str(bit) for bit in binary_input),
    }
    for recipe, score, binary_input in recommendations
]
st.dataframe(pd.DataFrame(encoding_rows), width="stretch")

st.write(
    "This demo maps meal context and recipe attributes into binary AO inputs, then lets the "
    "agent learn from lightweight positive or negative feedback. The fallback scorer keeps the "
    "demo reviewable without private AO package access."
)
