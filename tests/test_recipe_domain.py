import unittest

from recipe_domain import (
    DIETARY_FLAGS,
    MealContext,
    RECIPE_CATALOG,
    encode_recipe,
    recommend_recipes,
    score_recipe,
)


class RecipeDomainTest(unittest.TestCase):
    def test_encoder_has_expected_shape(self):
        context = MealContext("dinner", "balanced", 35)
        encoded = encode_recipe(RECIPE_CATALOG[0], context)
        self.assertEqual(len(encoded), 23)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_context_changes_binary_input(self):
        recipe = RECIPE_CATALOG[0]
        balanced = MealContext("dinner", "balanced", 35)
        adventurous = MealContext("dinner", "adventurous", 35)
        self.assertNotEqual(encode_recipe(recipe, balanced), encode_recipe(recipe, adventurous))

    def test_binary_input_includes_meal_context(self):
        recipe = RECIPE_CATALOG[0]
        dinner = MealContext("dinner", "balanced", 35)
        lunch = MealContext("lunch", "balanced", 35, "vegetarian")
        self.assertNotEqual(encode_recipe(recipe, dinner), encode_recipe(recipe, lunch))

    def test_dietary_preference_rewards_matching_recipes(self):
        vegetarian_context = MealContext("lunch", "quick", 30, "vegetarian")
        vegetarian_recipe = next(recipe for recipe in RECIPE_CATALOG if "vegetarian" in recipe.dietary_tags)
        non_matching_recipe = next(recipe for recipe in RECIPE_CATALOG if "vegetarian" not in recipe.dietary_tags)
        self.assertGreater(
            score_recipe(vegetarian_recipe, vegetarian_context),
            score_recipe(non_matching_recipe, vegetarian_context),
        )

    def test_recommendations_prioritize_requested_meal_and_time(self):
        context = MealContext("breakfast", "quick", 15, "vegetarian")
        top_recipe, top_score, _ = recommend_recipes(context, limit=1)[0]
        self.assertEqual(top_recipe.meal_slot, "breakfast")
        self.assertLessEqual(top_recipe.cook_time_minutes, 15)
        self.assertGreaterEqual(top_score, 70)

    def test_all_dietary_flags_are_representable(self):
        represented = {tag for recipe in RECIPE_CATALOG for tag in recipe.dietary_tags}
        self.assertTrue(set(DIETARY_FLAGS).issubset(represented))


if __name__ == "__main__":
    unittest.main()
