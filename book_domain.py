BOOK_CATALOG = [
    {
        "id": "project-hail-mary",
        "title": "Project Hail Mary",
        "genre": "science_fiction",
        "pace": "fast",
        "length": "long",
        "tone": "hopeful",
        "format": "novel",
        "context": ["curious", "adventurous"],
    },
    {
        "id": "atomic-habits",
        "title": "Atomic Habits",
        "genre": "self_improvement",
        "pace": "medium",
        "length": "medium",
        "tone": "practical",
        "format": "nonfiction",
        "context": ["focused", "motivated"],
    },
    {
        "id": "the-house-in-the-cerulean-sea",
        "title": "The House in the Cerulean Sea",
        "genre": "fantasy",
        "pace": "gentle",
        "length": "medium",
        "tone": "cozy",
        "format": "novel",
        "context": ["comfort", "relaxed"],
    },
    {
        "id": "educated",
        "title": "Educated",
        "genre": "memoir",
        "pace": "medium",
        "length": "medium",
        "tone": "reflective",
        "format": "nonfiction",
        "context": ["thoughtful", "resilient"],
    },
    {
        "id": "the-murderbot-diaries",
        "title": "All Systems Red",
        "genre": "science_fiction",
        "pace": "fast",
        "length": "short",
        "tone": "witty",
        "format": "novella",
        "context": ["fun", "adventurous"],
    },
    {
        "id": "braiding-sweetgrass",
        "title": "Braiding Sweetgrass",
        "genre": "nature",
        "pace": "gentle",
        "length": "long",
        "tone": "reflective",
        "format": "nonfiction",
        "context": ["thoughtful", "calm"],
    },
    {
        "id": "the-way-of-kings",
        "title": "The Way of Kings",
        "genre": "fantasy",
        "pace": "slow",
        "length": "long",
        "tone": "epic",
        "format": "novel",
        "context": ["immersive", "adventurous"],
    },
    {
        "id": "deep-work",
        "title": "Deep Work",
        "genre": "productivity",
        "pace": "medium",
        "length": "medium",
        "tone": "practical",
        "format": "nonfiction",
        "context": ["focused", "motivated"],
    },
    {
        "id": "legends-and-lattes",
        "title": "Legends & Lattes",
        "genre": "fantasy",
        "pace": "gentle",
        "length": "short",
        "tone": "cozy",
        "format": "novel",
        "context": ["comfort", "fun"],
    },
    {
        "id": "the-design-of-everyday-things",
        "title": "The Design of Everyday Things",
        "genre": "design",
        "pace": "medium",
        "length": "medium",
        "tone": "practical",
        "format": "nonfiction",
        "context": ["curious", "focused"],
    },
]

GENRES = [
    "science_fiction",
    "fantasy",
    "self_improvement",
    "memoir",
    "nature",
    "productivity",
    "design",
]
PACES = ["gentle", "medium", "fast", "slow"]
LENGTHS = ["short", "medium", "long"]
TONES = ["cozy", "hopeful", "practical", "reflective", "witty", "epic"]
FORMATS = ["novel", "novella", "nonfiction"]
MOODS = ["comfort", "curious", "focused", "fun", "adventurous", "thoughtful", "motivated", "relaxed", "calm", "immersive"]


def one_hot(value, choices):
    return [1 if value == choice else 0 for choice in choices]


def encode_book(book, mood="curious"):
    return (
        one_hot(book["genre"], GENRES)
        + one_hot(book["pace"], PACES)
        + one_hot(book["length"], LENGTHS)
        + one_hot(book["tone"], TONES)
        + one_hot(book["format"], FORMATS)
        + one_hot(mood, MOODS)
    )


def score_book(book, preferences):
    score = 0
    for field in ("genre", "pace", "length", "tone", "format"):
        wanted = preferences.get(field)
        if wanted and book[field] == wanted:
            score += 2
    mood = preferences.get("mood")
    if mood and mood in book["context"]:
        score += 3
    return score


def recommend_books(preferences, catalog=None, limit=3):
    catalog = catalog or BOOK_CATALOG
    ranked = sorted(
        catalog,
        key=lambda book: (score_book(book, preferences), book["title"]),
        reverse=True,
    )
    return ranked[:limit]


def binary_input_size():
    return len(encode_book(BOOK_CATALOG[0]))
