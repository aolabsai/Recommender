import unittest

from home_domain import (
    HOME_TASKS,
    apply_feedback,
    encode_home_task,
    recommend_home_tasks,
)


class HomeDomainTests(unittest.TestCase):
    def test_encoding_matches_ao_input_shape(self):
        task = HOME_TASKS[0]

        encoded = encode_home_task(task, goal="prevent-breakdowns")

        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_safety_goal_prioritizes_safety_tasks(self):
        ranked = recommend_home_tasks(goal="safety", minutes_available=45, limit=3)

        self.assertTrue(any(task.category == "safety" for task, _ in ranked))

    def test_low_time_budget_keeps_short_tasks_near_top(self):
        ranked = recommend_home_tasks(goal="clean-comfort", minutes_available=20, limit=5)

        self.assertTrue(all(task.minutes <= 45 for task, _ in ranked))

    def test_feedback_changes_ranking(self):
        baseline = recommend_home_tasks(goal="save-money", minutes_available=45, limit=1)[0][0]
        target = "Build a seasonal maintenance checklist"
        feedback = {}
        for _ in range(5):
            feedback = apply_feedback(feedback, target, liked=True)

        updated = recommend_home_tasks(
            goal="save-money",
            minutes_available=45,
            feedback=feedback,
            limit=1,
        )[0][0]

        self.assertNotEqual(baseline.name, updated.name)
        self.assertEqual(updated.name, target)

    def test_unknown_goal_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_home_tasks(goal="unknown")


if __name__ == "__main__":
    unittest.main()
