import unittest

from career_domain import (
    CAREER_ACTIONS,
    apply_feedback,
    encode_career_action,
    recommend_career_actions,
)


class CareerDomainTests(unittest.TestCase):
    def test_encoding_matches_ao_input_shape(self):
        action = CAREER_ACTIONS[0]

        encoded = encode_career_action(action, goal="restart-search")

        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_recommendations_prioritize_level_up_interview_or_negotiation(self):
        ranked = recommend_career_actions(goal="level-up", weekly_hours_available=6, limit=3)

        self.assertTrue(any(action.track in {"interview", "negotiation"} for action, _ in ranked))

    def test_low_time_budget_penalizes_deep_actions(self):
        ranked = recommend_career_actions(goal="restart-search", weekly_hours_available=1, limit=5)

        self.assertTrue(all(action.weekly_hours <= 4 for action, _ in ranked))

    def test_feedback_changes_ranking(self):
        baseline = recommend_career_actions(goal="first-role", weekly_hours_available=4, limit=1)[0][0]
        target = "Draft a negotiation script"
        feedback = apply_feedback({}, target, liked=True)
        feedback = apply_feedback(feedback, target, liked=True)
        feedback = apply_feedback(feedback, target, liked=True)
        feedback = apply_feedback(feedback, target, liked=True)

        updated = recommend_career_actions(
            goal="first-role",
            weekly_hours_available=4,
            feedback=feedback,
            limit=1,
        )[0][0]

        self.assertNotEqual(baseline.name, updated.name)
        self.assertEqual(updated.name, target)

    def test_unknown_goal_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_career_actions(goal="unknown")


if __name__ == "__main__":
    unittest.main()
