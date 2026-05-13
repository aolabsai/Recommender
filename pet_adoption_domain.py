"""Pet adoption recommendation domain for the AO recommender demo."""

from __future__ import annotations

from copy import deepcopy


SPECIES_ENCODINGS = {
    "any": [0, 0, 0],
    "dog": [0, 0, 1],
    "cat": [0, 1, 0],
    "rabbit": [0, 1, 1],
    "bird": [1, 0, 0],
    "small_mammal": [1, 0, 1],
}

ENERGY_ENCODINGS = {
    "low": [0, 0],
    "medium": [0, 1],
    "high": [1, 1],
}

GOAL_ENCODINGS = {
    "companion": [0, 0],
    "active": [0, 1],
    "family": [1, 0],
    "special_needs": [1, 1],
}

PET_CATALOG = [
    {
        "id": "luna",
        "name": "Luna",
        "species": "cat",
        "age": "adult",
        "energy": "low",
        "home_types": ["apartment", "house"],
        "good_with_children": False,
        "experience_required": "new",
        "goals": ["companion"],
        "traits": ["quiet", "lap_cat", "independent"],
        "description": "A calm adult cat who prefers quiet rooms and predictable routines.",
    },
    {
        "id": "ranger",
        "name": "Ranger",
        "species": "dog",
        "age": "young",
        "energy": "high",
        "home_types": ["house"],
        "good_with_children": True,
        "experience_required": "experienced",
        "goals": ["active"],
        "traits": ["hiking", "fetch", "training"],
        "description": "A trail-ready dog who wants structured exercise and confident handling.",
    },
    {
        "id": "poppy",
        "name": "Poppy",
        "species": "dog",
        "age": "adult",
        "energy": "medium",
        "home_types": ["house"],
        "good_with_children": True,
        "experience_required": "new",
        "goals": ["family"],
        "traits": ["gentle", "patient", "yard_play"],
        "description": "A gentle family dog who enjoys daily walks and backyard play.",
    },
    {
        "id": "milo",
        "name": "Milo",
        "species": "cat",
        "age": "young",
        "energy": "low",
        "home_types": ["apartment", "house"],
        "good_with_children": True,
        "experience_required": "new",
        "goals": ["family", "companion"],
        "traits": ["playful", "social", "easygoing"],
        "description": "A social cat who is comfortable with gentle children and mixed routines.",
    },
    {
        "id": "sage",
        "name": "Sage",
        "species": "rabbit",
        "age": "adult",
        "energy": "medium",
        "home_types": ["apartment", "house"],
        "good_with_children": True,
        "experience_required": "new",
        "goals": ["companion", "family"],
        "traits": ["litter_trained", "curious", "soft_handling"],
        "description": "A litter-trained rabbit for adopters who can provide supervised floor time.",
    },
    {
        "id": "kiwi",
        "name": "Kiwi",
        "species": "bird",
        "age": "adult",
        "energy": "medium",
        "home_types": ["apartment", "house"],
        "good_with_children": False,
        "experience_required": "experienced",
        "goals": ["companion"],
        "traits": ["vocal", "enrichment", "routine"],
        "description": "A bright companion bird who needs enrichment and an experienced caretaker.",
    },
    {
        "id": "peanut",
        "name": "Peanut",
        "species": "small_mammal",
        "age": "senior",
        "energy": "low",
        "home_types": ["apartment", "house"],
        "good_with_children": True,
        "experience_required": "new",
        "goals": ["companion", "special_needs"],
        "traits": ["senior", "low_space", "gentle"],
        "description": "A senior guinea pig who fits small homes and calm handling.",
    },
    {
        "id": "nova",
        "name": "Nova",
        "species": "dog",
        "age": "adult",
        "energy": "medium",
        "home_types": ["apartment", "house"],
        "good_with_children": False,
        "experience_required": "experienced",
        "goals": ["special_needs", "companion"],
        "traits": ["deaf", "visual_cues", "loyal"],
        "description": "A deaf dog who thrives with visual cue training and a steady home.",
    },
    {
        "id": "maple",
        "name": "Maple",
        "species": "cat",
        "age": "senior",
        "energy": "low",
        "home_types": ["apartment", "house"],
        "good_with_children": True,
        "experience_required": "new",
        "goals": ["special_needs", "family"],
        "traits": ["senior", "medication", "affectionate"],
        "description": "An affectionate senior cat whose adopter can keep a simple medication routine.",
    },
    {
        "id": "dash",
        "name": "Dash",
        "species": "rabbit",
        "age": "young",
        "energy": "high",
        "home_types": ["house"],
        "good_with_children": True,
        "experience_required": "experienced",
        "goals": ["active", "family"],
        "traits": ["agility", "enrichment", "supervised_play"],
        "description": "A high-energy rabbit for adopters who enjoy training and enrichment work.",
    },
    {
        "id": "opal",
        "name": "Opal",
        "species": "cat",
        "age": "adult",
        "energy": "medium",
        "home_types": ["apartment"],
        "good_with_children": False,
        "experience_required": "new",
        "goals": ["companion"],
        "traits": ["window_watching", "solo_pet", "curious"],
        "description": "A curious apartment cat who prefers being the only pet in a calm home.",
    },
    {
        "id": "buddy",
        "name": "Buddy",
        "species": "dog",
        "age": "senior",
        "energy": "low",
        "home_types": ["apartment", "house"],
        "good_with_children": True,
        "experience_required": "new",
        "goals": ["companion", "family"],
        "traits": ["senior", "short_walks", "calm"],
        "description": "A senior dog who wants short walks, soft beds, and a relaxed family.",
    },
]


def get_pet_by_id(pet_id):
    """Return a copy of a catalog pet by id."""
    for pet in PET_CATALOG:
        if pet["id"] == pet_id:
            return deepcopy(pet)
    raise ValueError(f"Unknown pet id: {pet_id}")


def encode_pet(pet, adoption_goal="companion"):
    """Encode pet attributes plus adopter goal into the 8-bit AO input shape."""
    _validate_option("species", pet["species"], SPECIES_ENCODINGS, allow_any=False)
    _validate_option("energy", pet["energy"], ENERGY_ENCODINGS)
    _validate_option("adoption_goal", adoption_goal, GOAL_ENCODINGS)

    child_bit = [1 if pet["good_with_children"] else 0]
    return (
        SPECIES_ENCODINGS[pet["species"]]
        + ENERGY_ENCODINGS[pet["energy"]]
        + child_bit
        + GOAL_ENCODINGS[adoption_goal]
    )


def rank_pets(
    preferred_species="any",
    home_type="apartment",
    activity_level="medium",
    has_children=False,
    experience_level="new",
    adoption_goal="companion",
    feedback=None,
    limit=5,
):
    """Rank adoptable pets for a household context using deterministic scoring."""
    _validate_option("preferred_species", preferred_species, SPECIES_ENCODINGS)
    _validate_option("activity_level", activity_level, ENERGY_ENCODINGS)
    _validate_option("adoption_goal", adoption_goal, GOAL_ENCODINGS)
    _validate_choice("home_type", home_type, {"apartment", "house"})
    _validate_choice("experience_level", experience_level, {"new", "experienced"})

    feedback = feedback or []
    scored = []
    for pet in PET_CATALOG:
        pet_copy = deepcopy(pet)
        score = _score_pet(
            pet_copy,
            preferred_species,
            home_type,
            activity_level,
            has_children,
            experience_level,
            adoption_goal,
        )
        score += _score_feedback_similarity(pet_copy, feedback)
        pet_copy["score"] = score
        pet_copy["binary_input"] = encode_pet(pet_copy, adoption_goal)
        scored.append(pet_copy)

    scored.sort(key=lambda item: (-item["score"], item["name"]))
    return scored[:limit]


def format_recommendations(recommendations):
    """Create compact CLI output for ranked pets."""
    lines = []
    for index, pet in enumerate(recommendations, start=1):
        traits = ", ".join(pet["traits"][:3])
        lines.append(
            f"{index}. {pet['name']} ({pet['species']}, score {pet['score']}): "
            f"{pet['description']} Traits: {traits}."
        )
    return "\n".join(lines)


def _score_pet(
    pet,
    preferred_species,
    home_type,
    activity_level,
    has_children,
    experience_level,
    adoption_goal,
):
    score = 0

    if preferred_species != "any":
        score += 5 if pet["species"] == preferred_species else -3

    score += 4 if home_type in pet["home_types"] else -6

    if pet["energy"] == activity_level:
        score += 4
    elif _energy_distance(pet["energy"], activity_level) == 1:
        score += 1
    else:
        score -= 2

    if has_children:
        score += 4 if pet["good_with_children"] else -7
    else:
        score += 1 if not pet["good_with_children"] else 0

    if pet["experience_required"] == "new":
        score += 3
    elif experience_level == "experienced":
        score += 3
    else:
        score -= 5

    if adoption_goal in pet["goals"]:
        score += 5
    elif adoption_goal == "family" and pet["good_with_children"]:
        score += 2
    elif adoption_goal == "active" and pet["energy"] == "high":
        score += 2

    return score


def _score_feedback_similarity(candidate, feedback):
    score = 0
    for event in feedback:
        pet_id = event.get("pet_id")
        if pet_id is None:
            continue

        reference_pet = get_pet_by_id(pet_id)
        direction = 1 if event.get("liked", True) else -1
        if candidate["id"] == reference_pet["id"]:
            score += 8 * direction
        if candidate["species"] == reference_pet["species"]:
            score += 2 * direction
        if candidate["energy"] == reference_pet["energy"]:
            score += direction
        if set(candidate["goals"]) & set(reference_pet["goals"]):
            score += direction
    return score


def _energy_distance(first, second):
    order = {"low": 0, "medium": 1, "high": 2}
    return abs(order[first] - order[second])


def _validate_option(name, value, options, allow_any=True):
    if value not in options or (value == "any" and not allow_any):
        raise ValueError(f"Invalid {name}: {value}")


def _validate_choice(name, value, choices):
    if value not in choices:
        raise ValueError(f"Invalid {name}: {value}")
