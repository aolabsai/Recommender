import unittest

from finance_domain import (
    FINANCE_ACTIONS,
    apply_feedback,
    encode_finance_action,
    recommend_finance_actions,
)


class FinanceDomainTests(unittest.TestCase):
    def test_encoding_matches_ao_input_shape(self):
        action = FINANCE_ACTIONS[0]

        encoded = encode_finance_action(action, goal="build-buffer")

        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_recommendations_prioritize_matching_goal(self):
        ranked = recommend_finance_actions(goal="grow-wealth", available_cash=200, limit=3)

        self.assertTrue(any(action.focus == "investing" for action, _ in ranked))

    def test_low_cash_penalizes_cash_negative_actions(self):
        low_cash = recommend_finance_actions(goal="grow-wealth", available_cash=0, limit=5)

        self.assertTrue(all(action.monthly_cash_impact >= -100 for action, _ in low_cash))

    def test_feedback_changes_ranking(self):
        baseline = recommend_finance_actions(goal="simplify", available_cash=100, limit=1)[0][0]
        feedback = apply_feedback({}, "Start a side-income experiment", liked=True)
        feedback = apply_feedback(feedback, "Start a side-income experiment", liked=True)
        feedback = apply_feedback(feedback, "Start a side-income experiment", liked=True)
        feedback = apply_feedback(feedback, "Start a side-income experiment", liked=True)

        updated = recommend_finance_actions(
            goal="simplify",
            available_cash=100,
            feedback=feedback,
            limit=1,
        )[0][0]

        self.assertNotEqual(baseline.name, updated.name)
        self.assertEqual(updated.name, "Start a side-income experiment")

    def test_unknown_goal_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_finance_actions(goal="unknown")


if __name__ == "__main__":
    unittest.main()
