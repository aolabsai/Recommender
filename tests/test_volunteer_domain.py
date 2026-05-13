import unittest

from volunteer_domain import (
    VOLUNTEER_CATALOG,
    VolunteerOpportunity,
    encode_opportunity,
    recommend_opportunities,
    score_opportunity,
)


class VolunteerDomainTest(unittest.TestCase):
    def test_encode_opportunity_uses_eight_bit_shape(self):
        encoded = encode_opportunity(VOLUNTEER_CATALOG[0], "high_impact")
        self.assertEqual(len(encoded), 8)
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_high_impact_goal_prefers_food_security(self):
        names = [item.name for item in recommend_opportunities("high_impact", max_time="short")]
        self.assertIn("Weekend Food Pantry Sort", names)

    def test_time_filter_penalizes_long_commitments(self):
        short_score = score_opportunity(VOLUNTEER_CATALOG[0], "high_impact", max_time="short")
        long_item = next(item for item in VOLUNTEER_CATALOG if item.time_commitment == "long")
        long_score = score_opportunity(long_item, "high_impact", max_time="short")
        self.assertGreater(short_score, long_score)

    def test_feedback_can_lift_preferred_category(self):
        recommendations = recommend_opportunities(
            "learn",
            feedback={"animal_welfare": 5},
            limit=1,
        )
        self.assertEqual(recommendations[0].category, "animal_welfare")

    def test_invalid_goal_raises(self):
        with self.assertRaises(ValueError):
            encode_opportunity(VOLUNTEER_CATALOG[0], "invalid")

    def test_invalid_category_raises(self):
        item = VolunteerOpportunity(
            "Bad Item",
            "unknown",
            "short",
            "beginner",
            "remote",
            "medium",
            "Invalid fixture.",
        )
        with self.assertRaises(ValueError):
            encode_opportunity(item, "learn")


if __name__ == "__main__":
    unittest.main()

