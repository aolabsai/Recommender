import unittest

from plant_domain import (
    PLANT_ACTIONS,
    apply_feedback,
    encode_plant_action,
    recommend_plant_actions,
)


class PlantDomainTests(unittest.TestCase):
    def test_encoding_matches_ao_input_shape(self):
        action = PLANT_ACTIONS[0]

        encoded = encode_plant_action(action, goal="easy-care")

        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_harvest_goal_prioritizes_herbs(self):
        ranked = recommend_plant_actions(goal="harvest", minutes_available=15, limit=3)

        self.assertTrue(any(action.plant_type == "herb" for action, _ in ranked))

    def test_low_time_budget_keeps_quick_actions_near_top(self):
        ranked = recommend_plant_actions(goal="easy-care", minutes_available=10, limit=5)

        self.assertTrue(all(action.minutes <= 20 for action, _ in ranked))

    def test_light_preference_changes_ranking(self):
        low_light_top = recommend_plant_actions(
            goal="faster-growth",
            indoor_light="low",
            minutes_available=20,
            limit=1,
        )[0][0]
        bright_light_top = recommend_plant_actions(
            goal="faster-growth",
            indoor_light="bright",
            minutes_available=20,
            limit=1,
        )[0][0]

        self.assertNotEqual(low_light_top.name, bright_light_top.name)

    def test_feedback_changes_ranking(self):
        baseline = recommend_plant_actions(goal="easy-care", minutes_available=15, limit=1)[0][0]
        target = "Flush mineral salts from soil"
        feedback = {}
        for _ in range(9):
            feedback = apply_feedback(feedback, target, liked=True)

        updated = recommend_plant_actions(
            goal="easy-care",
            minutes_available=15,
            feedback=feedback,
            limit=1,
        )[0][0]

        self.assertNotEqual(baseline.name, updated.name)
        self.assertEqual(updated.name, target)

    def test_unknown_goal_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_plant_actions(goal="unknown")


if __name__ == "__main__":
    unittest.main()
