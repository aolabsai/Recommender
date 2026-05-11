from __future__ import annotations

from dataclasses import dataclass
from math import ceil, log2


@dataclass(frozen=True)
class Recipe:
    title: str
    cuisine: str
    meal_slot: str
    cook_time_minutes: int
    difficulty: str
    dietary_tags: tuple[str, ...]
    contexts: tuple[str, ...]
    description: str
    ingredients: tuple[str, ...]


@dataclass(frozen=True)
class MealContext:
    meal_slot: str
    mood: str
    max_cook_time_minutes: int
    dietary_preference: str | None = None


CUISINES = (
    "american",
    "asian",
    "latin",
    "mediterranean",
    "middle_eastern",
    "indian",
    "bakery",
    "global",
)
MEAL_SLOTS = ("breakfast", "lunch", "dinner", "snack")
DIFFICULTIES = ("easy", "moderate", "project")
MOODS = ("quick", "comfort", "balanced", "adventurous")
DIETARY_FLAGS = ("vegetarian", "high_protein", "gluten_free", "dairy_free")


RECIPE_CATALOG = (
    Recipe(
        title="Miso Mushroom Rice Bowl",
        cuisine="asian",
        meal_slot="dinner",
        cook_time_minutes=28,
        difficulty="easy",
        dietary_tags=("vegetarian", "dairy_free"),
        contexts=("quick", "balanced"),
        description="Savory mushrooms, greens, and miso dressing over steamed rice.",
        ingredients=("mushrooms", "rice", "miso", "spinach", "sesame"),
    ),
    Recipe(
        title="Chickpea Shawarma Wraps",
        cuisine="middle_eastern",
        meal_slot="lunch",
        cook_time_minutes=24,
        difficulty="easy",
        dietary_tags=("vegetarian", "dairy_free"),
        contexts=("quick", "adventurous"),
        description="Roasted chickpeas, cucumber, herbs, and tahini in warm flatbread.",
        ingredients=("chickpeas", "flatbread", "tahini", "cucumber", "parsley"),
    ),
    Recipe(
        title="Turkey Chili with Black Beans",
        cuisine="american",
        meal_slot="dinner",
        cook_time_minutes=45,
        difficulty="moderate",
        dietary_tags=("high_protein", "gluten_free", "dairy_free"),
        contexts=("comfort", "balanced"),
        description="Weeknight chili with lean turkey, beans, tomatoes, and warm spices.",
        ingredients=("ground turkey", "black beans", "tomatoes", "chili powder"),
    ),
    Recipe(
        title="Lemon Herb Salmon Tray Bake",
        cuisine="mediterranean",
        meal_slot="dinner",
        cook_time_minutes=32,
        difficulty="easy",
        dietary_tags=("high_protein", "gluten_free", "dairy_free"),
        contexts=("balanced", "quick"),
        description="Salmon, potatoes, and green beans roasted on one tray.",
        ingredients=("salmon", "potatoes", "green beans", "lemon", "dill"),
    ),
    Recipe(
        title="Sweet Potato Breakfast Hash",
        cuisine="american",
        meal_slot="breakfast",
        cook_time_minutes=30,
        difficulty="moderate",
        dietary_tags=("gluten_free", "high_protein"),
        contexts=("comfort", "balanced"),
        description="Crisp sweet potatoes with peppers, onions, and eggs.",
        ingredients=("sweet potato", "eggs", "bell pepper", "onion"),
    ),
    Recipe(
        title="Mango Coconut Overnight Oats",
        cuisine="global",
        meal_slot="breakfast",
        cook_time_minutes=10,
        difficulty="easy",
        dietary_tags=("vegetarian", "dairy_free"),
        contexts=("quick", "balanced"),
        description="No-cook oats with mango, coconut milk, chia, and lime.",
        ingredients=("oats", "mango", "coconut milk", "chia", "lime"),
    ),
    Recipe(
        title="Lentil Bolognese",
        cuisine="mediterranean",
        meal_slot="dinner",
        cook_time_minutes=55,
        difficulty="moderate",
        dietary_tags=("vegetarian", "dairy_free", "high_protein"),
        contexts=("comfort", "balanced"),
        description="Rich tomato lentil sauce for pasta or roasted vegetables.",
        ingredients=("lentils", "tomatoes", "carrot", "celery", "pasta"),
    ),
    Recipe(
        title="Paneer Tikka Salad",
        cuisine="indian",
        meal_slot="lunch",
        cook_time_minutes=35,
        difficulty="moderate",
        dietary_tags=("vegetarian", "high_protein", "gluten_free"),
        contexts=("adventurous", "balanced"),
        description="Spiced paneer over greens with cucumber, tomato, and mint yogurt.",
        ingredients=("paneer", "yogurt", "greens", "cucumber", "garam masala"),
    ),
    Recipe(
        title="Avocado Edamame Toast",
        cuisine="global",
        meal_slot="snack",
        cook_time_minutes=12,
        difficulty="easy",
        dietary_tags=("vegetarian", "dairy_free", "high_protein"),
        contexts=("quick", "balanced"),
        description="Smashed avocado and edamame on toast with chili crisp.",
        ingredients=("bread", "avocado", "edamame", "lime", "chili crisp"),
    ),
    Recipe(
        title="Cocoa Tahini Energy Bites",
        cuisine="bakery",
        meal_slot="snack",
        cook_time_minutes=18,
        difficulty="easy",
        dietary_tags=("vegetarian", "gluten_free", "dairy_free"),
        contexts=("quick", "comfort"),
        description="No-bake bites with oats, tahini, cocoa, dates, and seeds.",
        ingredients=("oats", "tahini", "cocoa", "dates", "sunflower seeds"),
    ),
    Recipe(
        title="Black Bean Taco Skillet",
        cuisine="latin",
        meal_slot="dinner",
        cook_time_minutes=25,
        difficulty="easy",
        dietary_tags=("vegetarian", "gluten_free", "dairy_free"),
        contexts=("quick", "comfort"),
        description="A single-pan taco filling with black beans, corn, and salsa.",
        ingredients=("black beans", "corn", "salsa", "tortillas", "cilantro"),
    ),
    Recipe(
        title="Saffron Chickpea Pilaf",
        cuisine="middle_eastern",
        meal_slot="dinner",
        cook_time_minutes=50,
        difficulty="project",
        dietary_tags=("vegetarian", "gluten_free", "dairy_free"),
        contexts=("adventurous", "comfort"),
        description="Fragrant rice with chickpeas, herbs, raisins, and toasted nuts.",
        ingredients=("rice", "chickpeas", "saffron", "raisins", "almonds"),
    ),
)


def _option_bits(value: str, options: tuple[str, ...]) -> list[int]:
    normalized = value.lower()
    if normalized not in options:
        normalized = options[-1]
    bit_width = ceil(log2(len(options)))
    return [int(bit) for bit in format(options.index(normalized), f"0{bit_width}b")]


def _cook_time_bits(minutes: int) -> list[int]:
    if minutes <= 20:
        return [0, 0]
    if minutes <= 35:
        return [0, 1]
    if minutes <= 55:
        return [1, 0]
    return [1, 1]


def _dietary_preference_bits(preference: str | None) -> list[int]:
    return [int(preference == flag) for flag in DIETARY_FLAGS]


def encode_recipe(recipe: Recipe, context: MealContext) -> list[int]:
    return (
        _option_bits(recipe.cuisine, CUISINES)
        + _option_bits(recipe.meal_slot, MEAL_SLOTS)
        + _cook_time_bits(recipe.cook_time_minutes)
        + _option_bits(recipe.difficulty, DIFFICULTIES)
        + [int(flag in recipe.dietary_tags) for flag in DIETARY_FLAGS]
        + _option_bits(context.meal_slot, MEAL_SLOTS)
        + _cook_time_bits(context.max_cook_time_minutes)
        + _dietary_preference_bits(context.dietary_preference)
        + _option_bits(context.mood, MOODS)
    )


def score_recipe(recipe: Recipe, context: MealContext) -> int:
    score = 0
    if recipe.meal_slot == context.meal_slot:
        score += 35
    if context.mood in recipe.contexts:
        score += 25
    if recipe.cook_time_minutes <= context.max_cook_time_minutes:
        score += 20
    else:
        score -= min(25, recipe.cook_time_minutes - context.max_cook_time_minutes)
    if context.dietary_preference:
        if context.dietary_preference in recipe.dietary_tags:
            score += 20
        else:
            score -= 35
    if recipe.difficulty == "easy":
        score += 8
    elif recipe.difficulty == "project" and context.mood != "adventurous":
        score -= 10
    return max(0, min(100, score))


def recommend_recipes(
    context: MealContext,
    catalog: tuple[Recipe, ...] = RECIPE_CATALOG,
    limit: int = 5,
) -> list[tuple[Recipe, int, list[int]]]:
    ranked = [
        (recipe, score_recipe(recipe, context), encode_recipe(recipe, context))
        for recipe in catalog
    ]
    ranked.sort(key=lambda item: (-item[1], item[0].cook_time_minutes, item[0].title))
    return ranked[:limit]


def feedback_label(user_liked_recipe: bool, output_size: int) -> list[int]:
    return [1 if user_liked_recipe else 0] * output_size
