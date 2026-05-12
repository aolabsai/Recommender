from __future__ import annotations

import hashlib

import numpy as np
import pandas as pd
import streamlit as st

from music_domain import (
    MUSIC_CATALOG,
    encode_track,
    format_track_card,
    load_catalog_from_csv,
    pick_next_track,
    recommendation_percentage,
)

try:
    import ao_core as ao
    from arch__MusicRecommender import arch
except ImportError:
    ao = None
    arch = None


CONTEXTS = ("Surprise me", "Focus", "Workout", "Wind down")


def ensure_state() -> None:
    st.session_state.setdefault("music_catalog", MUSIC_CATALOG)
    st.session_state.setdefault("seen_music_titles", [])
    st.session_state.setdefault("music_index_seed", 0)
    st.session_state.setdefault("music_feedback_history", [])
    st.session_state.setdefault("current_track_bits", [])
    st.session_state.setdefault(
        "current_track",
        pick_next_track([], 0, st.session_state.music_catalog),
    )

    if "music_agent" not in st.session_state and ao is not None:
        st.session_state.music_agent = ao.Agent(arch, notes="Music Domain Agent")
        for _ in range(4):
            st.session_state.music_agent.reset_state()
            st.session_state.music_agent.reset_state(training=True)


def fallback_response(binary_input: list[int]) -> list[int]:
    score = sum(binary_input)
    return [1 if (score + idx) % 4 in (1, 2, 3) else 0 for idx in range(10)]


def agent_response(binary_input: list[int]) -> list[int]:
    if ao is None:
        return fallback_response(binary_input)

    st.session_state.music_agent.reset_state()
    response = None
    for _ in range(5):
        response = st.session_state.music_agent.next_state(
            INPUT=binary_input,
            print_result=False,
        )
    return response


def train_agent(user_response: str) -> None:
    if ao is None:
        return

    label_value = 1 if user_response == "Recommend more" else 0
    label = np.full(
        st.session_state.music_agent.arch.Z__flat.shape,
        label_value,
        dtype=np.int8,
    )
    repetitions = 6 if label_value else 10

    for _ in range(repetitions):
        st.session_state.music_agent.reset_state()
        st.session_state.music_agent.next_state(
            INPUT=st.session_state.current_track_bits,
            LABEL=label,
            print_result=False,
            unsequenced=True,
        )


def advance_track() -> None:
    st.session_state.seen_music_titles.append(st.session_state.current_track.title)
    st.session_state.music_index_seed += 1
    st.session_state.current_track = pick_next_track(
        st.session_state.seen_music_titles,
        st.session_state.music_index_seed,
        st.session_state.music_catalog,
    )


st.set_page_config(
    page_title="Music Recommender Demo by AO Labs",
    page_icon="misc/ao_favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

ensure_state()

with st.sidebar:
    st.write("## Music Dataset")
    st.write(f"{len(st.session_state.music_catalog)} tracks loaded")

    uploaded_catalog = st.file_uploader(
        "Use a custom music CSV",
        type=["csv"],
        help=(
            "Required columns: title, artist, genres, tempo_bpm, energy, "
            "release_year, vocal, summary. Separate multiple genres with semicolons."
        ),
    )
    if uploaded_catalog is not None:
        uploaded_bytes = uploaded_catalog.getvalue()
        catalog_hash = hashlib.sha256(uploaded_bytes).hexdigest()
        if catalog_hash != st.session_state.get("music_catalog_hash"):
            try:
                st.session_state.music_catalog = load_catalog_from_csv(
                    uploaded_bytes.decode("utf-8-sig")
                )
                st.session_state.music_catalog_hash = catalog_hash
                st.session_state.seen_music_titles = []
                st.session_state.music_index_seed = 0
                st.session_state.music_feedback_history = []
                st.session_state.current_track = pick_next_track(
                    [],
                    0,
                    st.session_state.music_catalog,
                )
                st.success(f"Loaded {len(st.session_state.music_catalog)} tracks")
            except UnicodeDecodeError:
                st.error("CSV must be UTF-8 encoded.")
            except ValueError as exc:
                st.error(str(exc))

    if ao is None:
        st.warning(
            "AO packages are not installed, so the app is using a deterministic local response. "
            "Install ao_core and ao_arch to train a live AO Agent."
        )
    elif st.button("Reset Music Agent"):
        del st.session_state.music_agent
        ensure_state()
        st.success("Music Agent reset")

st.title("Real-Time Personal Music Recommender")
st.write("A music-domain demo for AO Labs' continuously trainable recommender.")

context = st.selectbox("Set your current listening context:", CONTEXTS)
track = st.session_state.current_track
binary_input = encode_track(track, context)
st.session_state.current_track_bits = binary_input

response = agent_response(binary_input)
recommendation = recommendation_percentage(response)

left, right = st.columns([0.6, 0.4], gap="large")

with left:
    st.markdown(format_track_card(track))
    st.write(f"Agent recommendation: {recommendation}%")
    st.progress(recommendation)
    st.caption(f"Agent input bits: {binary_input}")

with right:
    if st.button("Recommend more", type="primary"):
        train_agent("Recommend more")
        st.session_state.music_feedback_history.append(
            [track.title, track.artist, context, recommendation, "Recommend more"]
        )
        advance_track()
        st.rerun()

    if st.button("Stop recommending"):
        train_agent("Stop recommending")
        st.session_state.music_feedback_history.append(
            [track.title, track.artist, context, recommendation, "Stop recommending"]
        )
        advance_track()
        st.rerun()

    if st.button("Skip"):
        st.session_state.music_feedback_history.append(
            [track.title, track.artist, context, recommendation, "Skipped"]
        )
        advance_track()
        st.rerun()

st.write("---")
st.write("### Training History")

if st.session_state.music_feedback_history:
    st.dataframe(
        pd.DataFrame(
            st.session_state.music_feedback_history,
            columns=["Title", "Artist", "Context", "Recommendation", "Feedback"],
        ),
        use_container_width=True,
    )
else:
    st.info("Rate a track to start training this music-domain agent.")
