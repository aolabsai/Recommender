"""Streamlit demo: AO-style travel experience recommender.

Run with:
    streamlit run travel_recommender.py
"""

from __future__ import annotations

import importlib

import pandas as pd
import streamlit as st

from travel_domain import (
    CATALOG,
    TravelExperience,
    TravelPreferences,
    encode_experience,
    rank_experiences,
    recommendation_percentage,
)


def _optional_ao_agent():
    """Create an AO Agent when ao_core is installed, otherwise return None."""

    try:
        ao = importlib.import_module("ao_core")
        arch_module = importlib.import_module("arch__Recommender")
    except Exception:
        return None

    try:
        agent = ao.Agent(arch_module.arch, notes="Travel Domain Agent")
        for _ in range(4):
            agent.reset_state()
            agent.reset_state(training=True)
        return agent
    except Exception:
        return None


def _agent_percentage(agent, binary_input: list[int]) -> int | None:
    if agent is None:
        return None

    try:
        agent.reset_state()
        response = None
        for _ in range(5):
            response = agent.next_state(INPUT=binary_input, print_result=False)
        if response is None:
            return None
        ones = sum(1 for value in response if value == 1)
        return round((ones / len(response)) * 100)
    except Exception:
        return None


def _train_agent(agent, binary_input: list[int], positive: bool) -> None:
    if agent is None:
        return

    try:
        import numpy as np

        label = (
            np.ones(agent.arch.Z__flat.shape, dtype=np.int8)
            if positive
            else np.zeros(agent.arch.Z__flat.shape, dtype=np.int8)
        )
        repetitions = 5 if positive else 10
        for _ in range(repetitions):
            agent.reset_state()
            agent.next_state(INPUT=binary_input, LABEL=label, print_result=False, unsequenced=True)
    except Exception as error:
        st.warning(f"AO Agent training was skipped: {error}")


def _ensure_state() -> None:
    defaults = {
        "travel_positive": [],
        "travel_negative": [],
        "travel_history": [],
        "travel_index": 0,
        "travel_agent": None,
        "travel_agent_checked": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    if not st.session_state.travel_agent_checked:
        st.session_state.travel_agent = _optional_ao_agent()
        st.session_state.travel_agent_checked = True


def _current_recommendation(
    preferences: TravelPreferences,
) -> tuple[TravelExperience, int, list[str], list[int], int | None]:
    ranked = rank_experiences(
        CATALOG,
        preferences,
        positive_feedback=st.session_state.travel_positive,
        negative_feedback=st.session_state.travel_negative,
    )
    selected = ranked[st.session_state.travel_index % len(ranked)]
    experience, fallback_score, reasons = selected
    binary_input = encode_experience(experience, preferences)
    ao_percentage = _agent_percentage(st.session_state.travel_agent, binary_input)
    fallback_percentage = recommendation_percentage(fallback_score)
    return experience, fallback_percentage, reasons, binary_input, ao_percentage


def _record_feedback(experience: TravelExperience, binary_input: list[int], positive: bool) -> None:
    target = "travel_positive" if positive else "travel_negative"
    st.session_state[target].extend([experience.id, experience.activity_type])
    _train_agent(st.session_state.travel_agent, binary_input, positive=positive)
    st.session_state.travel_history.append(
        {
            "experience": experience.name,
            "city": experience.city,
            "signal": "more" if positive else "less",
            "activity": experience.activity_type,
        }
    )
    st.session_state.travel_index = 0


def main() -> None:
    st.set_page_config(
        page_title="Travel Recommender by AO Labs",
        page_icon="misc/ao_favicon.png",
        layout="wide",
    )
    _ensure_state()

    st.title("Real-Time Personal Travel Recommender")
    st.write("A travel-domain AO recommender demo with a local fallback for reviewers.")

    with st.sidebar:
        st.write("## Traveler Context")
        mood = st.selectbox("Mood", ("curious", "relaxed", "active", "social"), index=0)
        max_budget = st.selectbox("Max budget", ("free", "low", "medium", "high"), index=2)
        pace = st.selectbox("Pace", ("calm", "balanced", "energetic"), index=1)
        party = st.selectbox("Travel party", ("solo", "couple", "family", "group"), index=0)

        st.write("---")
        if st.session_state.travel_agent is None:
            st.info("Running deterministic fallback. Install ao_core/ao_arch to train a live AO Agent.")
        else:
            st.success("AO Agent loaded; feedback trains the live agent.")

    preferences = TravelPreferences(
        mood=mood,
        max_budget=max_budget,
        pace=pace,
        party=party,
    )
    experience, fallback_percentage, reasons, binary_input, ao_percentage = _current_recommendation(preferences)
    displayed_percentage = ao_percentage if ao_percentage is not None else fallback_percentage

    left, right = st.columns([0.62, 0.38], gap="large")
    with left:
        st.subheader(experience.name)
        st.caption(f"{experience.city}, {experience.country}")
        st.write(experience.description)
        st.metric("Recommendation", f"{displayed_percentage}%")

        detail_rows = {
            "Activity": experience.activity_type,
            "Budget": experience.budget,
            "Pace": experience.pace,
            "Duration": f"{experience.duration_hours:g} hours",
            "Outdoor": "yes" if experience.outdoor else "no",
            "AO input bits": "".join(str(bit) for bit in binary_input),
        }
        st.dataframe(pd.DataFrame(detail_rows.items(), columns=["Field", "Value"]), hide_index=True)

    with right:
        st.write("## Why this matched")
        for reason in reasons:
            st.write(f"- {reason}")

        more, less = st.columns(2)
        if more.button("Recommend more like this", type="primary"):
            _record_feedback(experience, binary_input, positive=True)
            st.rerun()
        if less.button("Show less like this"):
            _record_feedback(experience, binary_input, positive=False)
            st.rerun()

        if st.button("Next recommendation"):
            st.session_state.travel_index += 1
            st.rerun()

    if st.session_state.travel_history:
        st.write("---")
        st.write("## Feedback History")
        st.dataframe(pd.DataFrame(st.session_state.travel_history), hide_index=True)


if __name__ == "__main__":
    main()
