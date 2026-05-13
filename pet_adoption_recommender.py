"""CLI and Streamlit demo for the pet adoption recommender domain."""

from __future__ import annotations

import argparse

from pet_adoption_domain import format_recommendations, rank_pets


def recommend(
    preferred_species="any",
    home_type="apartment",
    activity_level="medium",
    has_children=False,
    experience_level="new",
    adoption_goal="companion",
    feedback=None,
    limit=5,
):
    """Return ranked pets through the deterministic fallback recommender."""
    return rank_pets(
        preferred_species=preferred_species,
        home_type=home_type,
        activity_level=activity_level,
        has_children=has_children,
        experience_level=experience_level,
        adoption_goal=adoption_goal,
        feedback=feedback,
        limit=limit,
    )


def run_cli(argv=None):
    parser = argparse.ArgumentParser(description="Recommend adoptable pets for a home context.")
    parser.add_argument("--species", default="any", choices=["any", "dog", "cat", "rabbit", "bird", "small_mammal"])
    parser.add_argument("--home", default="apartment", choices=["apartment", "house"])
    parser.add_argument("--activity", default="medium", choices=["low", "medium", "high"])
    parser.add_argument("--children", action="store_true")
    parser.add_argument("--experience", default="new", choices=["new", "experienced"])
    parser.add_argument(
        "--goal",
        default="companion",
        choices=["companion", "active", "family", "special_needs"],
    )
    parser.add_argument("--liked-pet", action="append", default=[])
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    feedback = [{"pet_id": pet_id, "liked": True} for pet_id in args.liked_pet]
    recommendations = recommend(
        preferred_species=args.species,
        home_type=args.home,
        activity_level=args.activity,
        has_children=args.children,
        experience_level=args.experience,
        adoption_goal=args.goal,
        feedback=feedback,
        limit=args.limit,
    )
    print(format_recommendations(recommendations))


def run_streamlit():
    import streamlit as st

    st.title("Pet Adoption Recommender")
    st.caption("A local AO-compatible recommender domain for matching pets to adopter context.")

    preferred_species = st.selectbox("Species", ["any", "dog", "cat", "rabbit", "bird", "small_mammal"])
    home_type = st.radio("Home type", ["apartment", "house"], horizontal=True)
    activity_level = st.select_slider("Activity level", options=["low", "medium", "high"], value="medium")
    has_children = st.checkbox("Children in household")
    experience_level = st.radio("Adopter experience", ["new", "experienced"], horizontal=True)
    adoption_goal = st.selectbox("Adoption goal", ["companion", "active", "family", "special_needs"])
    liked_pet = st.multiselect(
        "Recommend more like",
        ["luna", "ranger", "poppy", "milo", "sage", "kiwi", "peanut", "nova", "maple", "dash", "opal", "buddy"],
    )

    feedback = [{"pet_id": pet_id, "liked": True} for pet_id in liked_pet]
    recommendations = recommend(
        preferred_species=preferred_species,
        home_type=home_type,
        activity_level=activity_level,
        has_children=has_children,
        experience_level=experience_level,
        adoption_goal=adoption_goal,
        feedback=feedback,
    )

    for pet in recommendations:
        st.subheader(f"{pet['name']} - {pet['species']} - score {pet['score']}")
        st.write(pet["description"])
        st.write("AO input:", pet["binary_input"])
        st.write("Traits:", ", ".join(pet["traits"]))


def _running_in_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
    except Exception:
        return False
    return get_script_run_ctx() is not None


if __name__ == "__main__":
    if _running_in_streamlit():
        run_streamlit()
    else:
        run_cli()
