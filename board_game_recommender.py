"""Board-game-night recommender demo.

Run as a CLI for deterministic review:

    python3 board_game_recommender.py --players 4 --mood social --minutes 60

Or launch the Streamlit UI:

    streamlit run board_game_recommender.py
"""

from __future__ import annotations

import argparse
from typing import Any

from board_game_domain import (
    BOARD_GAME_CATALOG,
    GAME_TYPES,
    TABLE_MOODS,
    encode_game,
    format_recommendations,
    recommend_games,
)


SAMPLE_FEEDBACK = [
    {
        "title": "Codenames",
        "game_type": "party",
        "mood": "social",
        "liked": True,
    },
    {
        "title": "Root",
        "game_type": "strategy",
        "mood": "competitive",
        "liked": False,
    },
]


def maybe_score_with_ao(binary_input: list[int]) -> float | None:
    """Return an AO score when optional AO packages are installed.

    The deterministic fallback keeps the demo reviewable without private packages,
    paid APIs, or network access.
    """

    try:
        import numpy as np
        import ao_core as ao

        from arch__BoardGameRecommender import arch
    except Exception:
        return None

    agent = ao.Agent(arch, notes="Board Game Night Recommender")
    agent.reset_state()
    response = None
    for _ in range(5):
        response = agent.next_state(INPUT=binary_input, print_result=False)
    if response is None:
        return None

    return round(float(np.count_nonzero(response)) / len(response) * 100, 2)


def build_context_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "players": args.players,
        "available_minutes": args.minutes,
        "mood": args.mood,
        "preferred_type": args.preferred_type,
        "complexity": args.complexity,
        "social_energy": args.social_energy,
        "want_teach_fast": args.fast_teach,
    }


def run_cli(args: argparse.Namespace) -> int:
    context = build_context_from_args(args)
    feedback = SAMPLE_FEEDBACK if args.with_sample_feedback else None
    recommendations = recommend_games(context, limit=args.limit, feedback=feedback)

    print("Board game night recommendations")
    print(f"Context: {context}")
    print()
    print(format_recommendations(recommendations))

    if args.show_ao_score and recommendations:
        game = next(
            item for item in BOARD_GAME_CATALOG if item.title == recommendations[0]["title"]
        )
        score = maybe_score_with_ao(encode_game(game, context))
        if score is None:
            print("\nAO packages unavailable; deterministic fallback ranking was used.")
        else:
            print(f"\nOptional AO Agent score for top pick: {score}%")

    return 0


def run_streamlit() -> None:
    try:
        import streamlit as st
    except Exception as exc:  # pragma: no cover - exercised manually
        raise SystemExit(
            "Streamlit is not installed. Use the CLI mode or install requirements.txt."
        ) from exc

    st.set_page_config(page_title="Board Game Night Recommender", layout="wide")
    st.title("Board Game Night Recommender")

    with st.sidebar:
        st.header("Group context")
        players = st.slider("Players", min_value=1, max_value=8, value=4)
        minutes = st.slider("Available minutes", min_value=30, max_value=180, value=90, step=15)
        mood = st.selectbox("Table mood", TABLE_MOODS, index=2)
        preferred_type = st.selectbox("Preferred style", [""] + GAME_TYPES, index=0)
        complexity = st.selectbox("Complexity", ["any", "light", "medium", "heavy"], index=0)
        social_energy = st.selectbox("Social energy", ["low", "medium", "high"], index=1)
        fast_teach = st.checkbox("Need a quick teach")
        use_feedback = st.checkbox("Apply sample feedback")

    context = {
        "players": players,
        "available_minutes": minutes,
        "mood": mood,
        "preferred_type": preferred_type,
        "complexity": complexity,
        "social_energy": social_energy,
        "want_teach_fast": fast_teach,
    }
    feedback = SAMPLE_FEEDBACK if use_feedback else None

    rows = recommend_games(context, feedback=feedback)
    st.write("### Recommendations")
    for row in rows:
        st.write(f"**{row['title']}** - score `{row['score']}`")
        st.caption(row["reason"])
        st.code("".join(str(bit) for bit in row["binary_input"]), language="text")

    if rows:
        game = next(item for item in BOARD_GAME_CATALOG if item.title == rows[0]["title"])
        score = maybe_score_with_ao(encode_game(game, context))
        if score is not None:
            st.info(f"Optional AO Agent score for top pick: {score}%")
        else:
            st.caption("AO packages were not found, so deterministic fallback ranking is active.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recommend board games for a group.")
    parser.add_argument("--players", type=int, default=4)
    parser.add_argument("--minutes", type=int, default=90)
    parser.add_argument("--mood", choices=TABLE_MOODS, default="social")
    parser.add_argument("--preferred-type", choices=[""] + GAME_TYPES, default="")
    parser.add_argument("--complexity", choices=["any", "light", "medium", "heavy"], default="any")
    parser.add_argument("--social-energy", choices=["low", "medium", "high"], default="medium")
    parser.add_argument("--fast-teach", action="store_true")
    parser.add_argument("--with-sample-feedback", action="store_true")
    parser.add_argument("--show-ao-score", action="store_true")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--streamlit", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.streamlit:
        run_streamlit()
        return 0
    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
