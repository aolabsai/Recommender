from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple


GENRE_BUCKETS = {
    "comedy": 0,
    "drama": 1,
    "action": 2,
    "documentary": 3,
    "animation": 4,
    "romance": 5,
    "sci-fi": 6,
    "thriller": 7,
}

MOOD_BUCKETS = {
    "surprise me": [0, 0],
    "easy watch": [0, 1],
    "focused": [1, 0],
    "high energy": [1, 1],
}


@dataclass(frozen=True)
class MovieCandidate:
    title: str
    genres: Tuple[str, ...]
    year: int
    runtime_minutes: int
    rating: float
    summary: str


MOVIE_CATALOG: Tuple[MovieCandidate, ...] = (
    MovieCandidate(
        "Midnight Market",
        ("drama", "romance"),
        2019,
        102,
        7.4,
        "A quiet city drama about two vendors rebuilding trust across one summer.",
    ),
    MovieCandidate(
        "Signal Runner",
        ("action", "thriller"),
        2021,
        118,
        7.7,
        "A courier races through a locked-down city with evidence of a conspiracy.",
    ),
    MovieCandidate(
        "Ocean Almanac",
        ("documentary",),
        2018,
        83,
        8.1,
        "Marine researchers track reef recovery and the people protecting it.",
    ),
    MovieCandidate(
        "The Clockwork Orchard",
        ("animation", "sci-fi"),
        2022,
        94,
        8.0,
        "A family-friendly animated adventure through a mechanical forest.",
    ),
    MovieCandidate(
        "Kitchen Fires",
        ("comedy", "drama"),
        2020,
        98,
        7.2,
        "A chaotic restaurant crew tries to survive opening night.",
    ),
    MovieCandidate(
        "Northbound Static",
        ("sci-fi", "thriller"),
        2024,
        126,
        7.9,
        "Astronauts hear a repeating signal that should not exist.",
    ),
    MovieCandidate(
        "Postcard Weather",
        ("romance", "comedy"),
        2016,
        91,
        7.0,
        "Two rival travel writers trade cities and accidentally trade lives.",
    ),
    MovieCandidate(
        "Last Train Audit",
        ("documentary", "thriller"),
        2023,
        88,
        7.6,
        "An investigative documentary follows a transit fraud case in real time.",
    ),
    MovieCandidate(
        "Blue Circuit",
        ("action", "sci-fi"),
        2017,
        112,
        7.3,
        "A robotics engineer has one night to stop a runaway defense prototype.",
    ),
    MovieCandidate(
        "Small Town Orbit",
        ("comedy",),
        2015,
        86,
        6.9,
        "A local science fair spirals into a county-wide spectacle.",
    ),
    MovieCandidate(
        "Paper Lantern Season",
        ("drama",),
        2022,
        107,
        8.2,
        "Three siblings return home for a festival and settle unfinished business.",
    ),
    MovieCandidate(
        "The Violet Door",
        ("thriller",),
        2020,
        99,
        7.5,
        "A missing-room mystery unfolds inside a century-old hotel.",
    ),
)


def to_bits(value: int, width: int) -> List[int]:
    if value < 0:
        raise ValueError("value must be non-negative")
    if value >= 2**width:
        raise ValueError("value does not fit in requested bit width")
    return [int(bit) for bit in format(value, f"0{width}b")]


def normalize_mood(mood: str) -> str:
    normalized = mood.strip().lower()
    if normalized not in MOOD_BUCKETS:
        return "surprise me"
    return normalized


def primary_genre(movie: MovieCandidate) -> str:
    for genre in movie.genres:
        if genre in GENRE_BUCKETS:
            return genre
    return "comedy"


def runtime_bucket(runtime_minutes: int) -> int:
    if runtime_minutes < 95:
        return 0
    if runtime_minutes < 115:
        return 1
    if runtime_minutes < 135:
        return 2
    return 3


def recency_bucket(year: int) -> int:
    return 1 if year >= 2020 else 0


def rating_bucket(rating: float) -> int:
    return 1 if rating >= 7.5 else 0


def encode_movie(movie: MovieCandidate, mood: str) -> List[int]:
    return (
        to_bits(GENRE_BUCKETS[primary_genre(movie)], 3)
        + to_bits(runtime_bucket(movie.runtime_minutes), 2)
        + [recency_bucket(movie.year)]
        + [rating_bucket(movie.rating)]
        + MOOD_BUCKETS[normalize_mood(mood)]
    )


def recommendation_percentage(agent_output: Sequence[int]) -> int:
    if not agent_output:
        return 0
    positive = sum(1 for value in agent_output if value == 1)
    return round((positive / len(agent_output)) * 100)


def pick_next_movie(seen_titles: Iterable[str], index_seed: int = 0) -> MovieCandidate:
    seen = set(seen_titles)
    unseen = [movie for movie in MOVIE_CATALOG if movie.title not in seen]
    candidates = unseen or list(MOVIE_CATALOG)
    return candidates[index_seed % len(candidates)]


def format_movie_card(movie: MovieCandidate) -> str:
    genres = ", ".join(movie.genres)
    return (
        f"**{movie.title}** ({movie.year})\n\n"
        f"{genres} | {movie.runtime_minutes} min | {movie.rating:.1f}/10\n\n"
        f"{movie.summary}"
    )
