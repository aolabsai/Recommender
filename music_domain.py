from __future__ import annotations

import csv
from dataclasses import dataclass
from io import StringIO
from typing import Iterable, List, Sequence, Tuple


GENRE_BUCKETS = {
    "pop": 0,
    "hip-hop": 1,
    "electronic": 2,
    "rock": 3,
    "jazz": 4,
    "r&b": 5,
    "folk": 6,
    "classical": 7,
}

LISTENING_CONTEXTS = {
    "surprise me": [0, 0],
    "focus": [0, 1],
    "workout": [1, 0],
    "wind down": [1, 1],
}


@dataclass(frozen=True)
class TrackCandidate:
    title: str
    artist: str
    genres: Tuple[str, ...]
    tempo_bpm: int
    energy: int
    release_year: int
    vocal: bool
    summary: str


CSV_REQUIRED_COLUMNS = (
    "title",
    "artist",
    "genres",
    "tempo_bpm",
    "energy",
    "release_year",
    "vocal",
    "summary",
)


MUSIC_CATALOG: Tuple[TrackCandidate, ...] = (
    TrackCandidate(
        "City Lights After Midnight",
        "North Pier",
        ("electronic", "pop"),
        118,
        8,
        2023,
        False,
        "Bright synth pulses for late-night momentum without lyrics.",
    ),
    TrackCandidate(
        "Paper Planets",
        "Mara Vale",
        ("folk", "pop"),
        92,
        4,
        2021,
        True,
        "Warm acoustic storytelling with soft percussion and close vocals.",
    ),
    TrackCandidate(
        "Baseline Sketches",
        "The Static Notes",
        ("jazz",),
        136,
        6,
        2018,
        False,
        "A nimble trio piece built around upright bass and brushed drums.",
    ),
    TrackCandidate(
        "Highway Glass",
        "Signal Choir",
        ("rock",),
        154,
        9,
        2020,
        True,
        "Guitar-driven road-song energy with a big final chorus.",
    ),
    TrackCandidate(
        "Soft Reset",
        "Luma Drift",
        ("r&b", "electronic"),
        86,
        3,
        2024,
        True,
        "Low-tempo vocals and ambient pads for decompressing.",
    ),
    TrackCandidate(
        "Assembly Line Sunrise",
        "Metro Form",
        ("hip-hop",),
        98,
        7,
        2022,
        True,
        "Percussive verses with a steady bounce and clean hook.",
    ),
    TrackCandidate(
        "Window Seat Etude",
        "Iris Calder",
        ("classical",),
        72,
        2,
        2017,
        False,
        "Solo piano with a restrained melodic arc for quiet focus.",
    ),
    TrackCandidate(
        "Neon Shortcut",
        "Byte Harbor",
        ("electronic", "hip-hop"),
        128,
        8,
        2025,
        False,
        "A short instrumental loop with punchy drums and arcade textures.",
    ),
    TrackCandidate(
        "Hollow Gold",
        "June Relay",
        ("pop", "r&b"),
        104,
        5,
        2019,
        True,
        "Mid-tempo vocal pop with polished harmonies and a mellow groove.",
    ),
    TrackCandidate(
        "Field Recording No. 3",
        "Orchard Static",
        ("folk", "classical"),
        78,
        2,
        2020,
        False,
        "A sparse chamber-folk instrumental with natural room tone.",
    ),
    TrackCandidate(
        "Switchback",
        "Redline Theory",
        ("rock", "electronic"),
        142,
        9,
        2024,
        True,
        "Aggressive drums, distorted bass, and a fast vocal hook.",
    ),
    TrackCandidate(
        "Blue Hour Receipt",
        "Kei Santos",
        ("jazz", "r&b"),
        88,
        4,
        2022,
        True,
        "Smoky keys and relaxed vocals for a late-evening queue.",
    ),
)


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "vocal"}:
        return True
    if normalized in {"0", "false", "no", "n", "instrumental"}:
        return False
    raise ValueError(f"invalid vocal value: {value!r}")


def _parse_genres(value: str) -> Tuple[str, ...]:
    delimiter = ";" if ";" in value else "|" if "|" in value else ","
    genres = tuple(
        genre.strip().lower()
        for genre in value.split(delimiter)
        if genre.strip()
    )
    if not genres:
        raise ValueError("genres must include at least one genre")
    return genres


def load_catalog_from_csv(csv_text: str) -> Tuple[TrackCandidate, ...]:
    reader = csv.DictReader(StringIO(csv_text.strip()))
    if not reader.fieldnames:
        raise ValueError("CSV must include a header row")

    normalized_fields = {field.strip().lower() for field in reader.fieldnames}
    missing = [column for column in CSV_REQUIRED_COLUMNS if column not in normalized_fields]
    if missing:
        raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")

    tracks: list[TrackCandidate] = []
    for row_number, row in enumerate(reader, start=2):
        normalized_row = {
            (key or "").strip().lower(): (value or "").strip()
            for key, value in row.items()
        }
        try:
            title = normalized_row["title"]
            artist = normalized_row["artist"]
            if not title or not artist:
                raise ValueError("title and artist are required")

            tempo_bpm = int(normalized_row["tempo_bpm"])
            energy = int(normalized_row["energy"])
            release_year = int(normalized_row["release_year"])
            if tempo_bpm <= 0:
                raise ValueError("tempo_bpm must be positive")
            if energy < 0 or energy > 10:
                raise ValueError("energy must be between 0 and 10")

            tracks.append(
                TrackCandidate(
                    title=title,
                    artist=artist,
                    genres=_parse_genres(normalized_row["genres"]),
                    tempo_bpm=tempo_bpm,
                    energy=energy,
                    release_year=release_year,
                    vocal=_parse_bool(normalized_row["vocal"]),
                    summary=normalized_row["summary"],
                )
            )
        except ValueError as exc:
            raise ValueError(f"row {row_number}: {exc}") from exc

    if not tracks:
        raise ValueError("CSV must include at least one track")
    return tuple(tracks)


def to_bits(value: int, width: int) -> List[int]:
    if value < 0:
        raise ValueError("value must be non-negative")
    if value >= 2**width:
        raise ValueError("value does not fit in requested bit width")
    return [int(bit) for bit in format(value, f"0{width}b")]


def normalize_context(context: str) -> str:
    normalized = context.strip().lower()
    if normalized not in LISTENING_CONTEXTS:
        return "surprise me"
    return normalized


def primary_genre(track: TrackCandidate) -> str:
    for genre in track.genres:
        if genre in GENRE_BUCKETS:
            return genre
    return "pop"


def tempo_bucket(tempo_bpm: int) -> int:
    if tempo_bpm < 90:
        return 0
    if tempo_bpm < 115:
        return 1
    if tempo_bpm < 140:
        return 2
    return 3


def energy_bucket(energy: int) -> int:
    if energy < 4:
        return 0
    if energy < 7:
        return 1
    if energy < 9:
        return 2
    return 3


def recency_bucket(release_year: int) -> int:
    return 1 if release_year >= 2021 else 0


def vocal_bucket(vocal: bool) -> int:
    return 1 if vocal else 0


def encode_track(track: TrackCandidate, context: str) -> List[int]:
    return (
        to_bits(GENRE_BUCKETS[primary_genre(track)], 3)
        + to_bits(tempo_bucket(track.tempo_bpm), 2)
        + to_bits(energy_bucket(track.energy), 2)
        + [recency_bucket(track.release_year)]
        + [vocal_bucket(track.vocal)]
        + LISTENING_CONTEXTS[normalize_context(context)]
    )


def recommendation_percentage(agent_output: Sequence[int]) -> int:
    if not agent_output:
        return 0
    positive = sum(1 for value in agent_output if value == 1)
    return round((positive / len(agent_output)) * 100)


def pick_next_track(
    seen_titles: Iterable[str],
    index_seed: int = 0,
    catalog: Sequence[TrackCandidate] = MUSIC_CATALOG,
) -> TrackCandidate:
    if not catalog:
        raise ValueError("catalog must include at least one track")
    seen = set(seen_titles)
    unseen = [track for track in catalog if track.title not in seen]
    candidates = unseen or list(catalog)
    return candidates[index_seed % len(candidates)]


def format_track_card(track: TrackCandidate) -> str:
    genres = ", ".join(track.genres)
    vocal_text = "vocal" if track.vocal else "instrumental"
    return (
        f"**{track.title}** by {track.artist} ({track.release_year})\n\n"
        f"{genres} | {track.tempo_bpm} BPM | energy {track.energy}/10 | {vocal_text}\n\n"
        f"{track.summary}"
    )
