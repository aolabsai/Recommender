import unittest

from travel_domain import CATALOG, TravelPreferences, encode_experience, rank_experiences


class TravelDomainTest(unittest.TestCase):
    def test_encoding_matches_existing_ao_architecture_width(self):
        preferences = TravelPreferences(mood="active")
        encoded = encode_experience(CATALOG[0], preferences)

        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_budget_filter_penalizes_over_budget_experiences(self):
        preferences = TravelPreferences(mood="active", max_budget="low", pace="energetic")
        ranked = rank_experiences(CATALOG, preferences)

        top_five = [experience for experience, _, _ in ranked[:5]]
        self.assertTrue(all(experience.budget in {"free", "low"} for experience in top_five))

    def test_positive_feedback_promotes_activity_type(self):
        preferences = TravelPreferences(mood="curious", max_budget="medium", pace="balanced")
        baseline = rank_experiences(CATALOG, preferences)
        promoted = rank_experiences(CATALOG, preferences, positive_feedback=["nightlife"])

        baseline_best_nightlife = min(
            index
            for index, (experience, _, _) in enumerate(baseline)
            if experience.activity_type == "nightlife"
        )
        promoted_best_nightlife = min(
            index
            for index, (experience, _, _) in enumerate(promoted)
            if experience.activity_type == "nightlife"
        )
        self.assertLess(promoted_best_nightlife, baseline_best_nightlife)

    def test_negative_feedback_suppresses_specific_experience(self):
        preferences = TravelPreferences(mood="relaxed", max_budget="medium", pace="calm")
        target = "reykjavik-geothermal-dip"
        ranked = rank_experiences(CATALOG, preferences, negative_feedback=[target])

        target_rank = next(
            index for index, (experience, _, _) in enumerate(ranked) if experience.id == target
        )
        self.assertGreater(target_rank, 2)


if __name__ == "__main__":
    unittest.main()
