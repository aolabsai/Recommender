import unittest

from fitness_domain import (
    INPUT_WIDTH,
    WORKOUT_CATALOG,
    encode_workout,
    normalize_context,
    recommend_workouts,
)


class FitnessDomainTests(unittest.TestCase):
    def test_catalog_ids_are_unique(self):
        ids = [workout.id for workout in WORKOUT_CATALOG]
        self.assertEqual(len(ids), len(set(ids)))

    def test_encode_workout_uses_declared_input_width(self):
        bits = encode_workout(
            WORKOUT_CATALOG[0],
            {
                "goal": "mobility",
                "energy": "low",
                "time_budget_min": 15,
                "equipment": "none",
            },
        )
        self.assertEqual(len(bits), INPUT_WIDTH)
        self.assertTrue(all(bit in (0, 1) for bit in bits))

    def test_normalize_context_falls_back_for_unknown_values(self):
        context = normalize_context(
            {
                "goal": "powerlifting",
                "energy": "sleepy",
                "time_budget_min": "not-a-number",
                "equipment": "kettlebell",
            }
        )
        self.assertEqual(
            context,
            {
                "goal": "strength",
                "energy": "medium",
                "time_budget_min": 30,
                "equipment": "none",
            },
        )

    def test_recommender_prioritizes_matching_goal_equipment_and_time(self):
        recommendations = recommend_workouts(
            {
                "goal": "strength",
                "energy": "medium",
                "time_budget_min": 30,
                "equipment": "dumbbells",
            },
            limit=3,
        )
        top_workout = recommendations[0][0]
        self.assertEqual(top_workout.goal, "strength")
        self.assertEqual(top_workout.equipment, "dumbbells")
        self.assertLessEqual(top_workout.duration_min, 30)

    def test_recommender_can_run_with_no_equipment_constraint(self):
        recommendations = recommend_workouts(
            {
                "goal": "cardio",
                "energy": "high",
                "time_budget_min": 20,
                "equipment": "none",
            },
            limit=2,
        )
        self.assertGreaterEqual(len(recommendations), 2)
        self.assertEqual(recommendations[0][0].goal, "cardio")
        self.assertEqual(recommendations[0][0].equipment, "none")


if __name__ == "__main__":
    unittest.main()

