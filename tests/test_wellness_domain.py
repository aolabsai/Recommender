import unittest

from wellness_domain import (
    WELLNESS_HABITS,
    apply_feedback,
    encode_wellness_habit,
    recommend_wellness_habits,
)


class WellnessDomainTests(unittest.TestCase):
    def test_encoding_matches_ao_input_shape(self):
        habit = WELLNESS_HABITS[0]

        encoded = encode_wellness_habit(habit, goal="calm")

        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_sleep_goal_prioritizes_sleep_or_reflection(self):
        ranked = recommend_wellness_habits(
            goal="better-sleep",
            minutes_available=20,
            limit=3,
        )

        self.assertTrue(
            any(habit.focus in {"sleep", "reflection", "stress"} for habit, _ in ranked)
        )

    def test_deep_work_goal_prioritizes_focus(self):
        ranked = recommend_wellness_habits(goal="deep-work", minutes_available=30, limit=3)

        self.assertTrue(any(habit.focus == "focus" for habit, _ in ranked))

    def test_social_filter_penalizes_social_habits(self):
        ranked = recommend_wellness_habits(
            goal="reset",
            minutes_available=20,
            social_ok=False,
            limit=5,
        )

        self.assertTrue(all(not habit.social for habit, _ in ranked[:3]))

    def test_feedback_changes_ranking(self):
        baseline = recommend_wellness_habits(goal="calm", minutes_available=15, limit=1)[0][0]
        target = "Long-form weekly reset"
        feedback = {}
        for _ in range(10):
            feedback = apply_feedback(feedback, target, liked=True)

        updated = recommend_wellness_habits(
            goal="calm",
            minutes_available=15,
            feedback=feedback,
            limit=1,
        )[0][0]

        self.assertNotEqual(baseline.name, updated.name)
        self.assertEqual(updated.name, target)

    def test_unknown_goal_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_wellness_habits(goal="unknown")


if __name__ == "__main__":
    unittest.main()
