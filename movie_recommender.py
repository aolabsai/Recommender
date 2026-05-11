from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from movie_domain import (
    MOVIE_CATALOG,
    encode_movie,
    format_movie_card,
    pick_next_movie,
    recommendation_percentage,
)

try:
    import ao_core as ao
    from arch__MovieRecommender import arch
except ImportError:
    ao = None
    arch = None


MOODS = ("Surprise me", "Easy watch", "Focused", "High energy")


def ensure_state() -> None:
    st.session_state.setdefault("seen_movie_titles", [])
    st.session_state.setdefault("movie_index_seed", 0)
    st.session_state.setdefault("movie_feedback_history", [])
    st.session_state.setdefault("current_movie_bits", [])
    st.session_state.setdefault("current_movie", pick_next_movie([], 0))

    if "movie_agent" not in st.session_state and ao is not None:
        st.session_state.movie_agent = ao.Agent(arch, notes="Movie Domain Agent")
        for _ in range(4):
            st.session_state.movie_agent.reset_state()
            st.session_state.movie_agent.reset_state(training=True)


def fallback_response(binary_input: list[int]) -> list[int]:
    score = sum(binary_input)
    return [1 if (score + idx) % 3 != 0 else 0 for idx in range(10)]


def agent_response(binary_input: list[int]) -> list[int]:
    if ao is None:
        return fallback_response(binary_input)

    st.session_state.movie_agent.reset_state()
    response = None
    for _ in range(5):
        response = st.session_state.movie_agent.next_state(
            INPUT=binary_input,
            print_result=False,
        )
    return response


def train_agent(user_response: str) -> None:
    if ao is None:
        return

    label_value = 1 if user_response == "Recommend more" else 0
    label = np.full(
        st.session_state.movie_agent.arch.Z__flat.shape,
        label_value,
        dtype=np.int8,
    )
    repetitions = 6 if label_value else 10

    for _ in range(repetitions):
        st.session_state.movie_agent.reset_state()
        st.session_state.movie_agent.next_state(
            INPUT=st.session_state.current_movie_bits,
            LABEL=label,
            print_result=False,
            unsequenced=True,
        )


def advance_movie() -> None:
    st.session_state.seen_movie_titles.append(st.session_state.current_movie.title)
    st.session_state.movie_index_seed += 1
    st.session_state.current_movie = pick_next_movie(
        st.session_state.seen_movie_titles,
        st.session_state.movie_index_seed,
    )


st.set_page_config(
    page_title="Movie Recommender Demo by AO Labs",
    page_icon="misc/ao_favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_state()

with st.sidebar:
    st.write("## Movie Dataset")
    st.write(f"{len(MOVIE_CATALOG)} sample titles")
    if ao is None:
        st.warning(
            "AO packages are not installed, so the app is using a deterministic local response. "
            "Install ao_core and ao_arch to train a live AO Agent."
        )
    elif st.button("Reset Movie Agent"):
        del st.session_state.movie_agent
        ensure_state()
        st.success("Movie Agent reset")

st.title("Real-Time Personal Movie Recommender")
st.write("A second domain demo for AO Labs' continuously trainable recommender.")

mood = st.selectbox("Set your current viewing mood:", MOODS)
movie = st.session_state.current_movie
binary_input = encode_movie(movie, mood)
st.session_state.current_movie_bits = binary_input

response = agent_response(binary_input)
recommendation = recommendation_percentage(response)

left, right = st.columns([0.6, 0.4], gap="large")

with left:
    st.markdown(format_movie_card(movie))
    st.write(f"Agent recommendation: {recommendation}%")
    st.progress(recommendation)
    st.caption(f"Agent input bits: {binary_input}")

with right:
    if st.button("Recommend more", type="primary"):
        train_agent("Recommend more")
        st.session_state.movie_feedback_history.append(
            [movie.title, mood, recommendation, "Recommend more"]
        )
        advance_movie()
        st.rerun()

    if st.button("Stop recommending"):
        train_agent("Stop recommending")
        st.session_state.movie_feedback_history.append(
            [movie.title, mood, recommendation, "Stop recommending"]
        )
        advance_movie()
        st.rerun()

    if st.button("Skip"):
        st.session_state.movie_feedback_history.append(
            [movie.title, mood, recommendation, "Skipped"]
        )
        advance_movie()
        st.rerun()

st.write("---")
st.write("### Training History")

if st.session_state.movie_feedback_history:
    st.dataframe(
        pd.DataFrame(
            st.session_state.movie_feedback_history,
            columns=["Title", "Mood", "Recommendation", "Feedback"],
        ),
        use_container_width=True,
    )
else:
    st.info("Rate a title to start training this movie-domain agent.")
