import unittest

from learning_domain import (
    LEARNING_CATALOG,
    encode_learning_resource,
    format_learning_card,
    pick_next_learning_resource,
    recommendation_percentage,
)


class LearningDomainTests(unittest.TestCase):
    def test_catalog_titles_are_unique(self):
        titles = [resource.title for resource in LEARNING_CATALOG]
        self.assertEqual(len(titles), len(set(titles)))

    def test_encode_learning_resource_returns_binary_features(self):
        bits = encode_learning_resource(LEARNING_CATALOG[0], "Ship a prototype")
        self.assertEqual(len(bits), 12)
        self.assertTrue(all(bit in (0, 1) for bit in bits))

    def test_encode_learning_resource_is_deterministic(self):
        resource = LEARNING_CATALOG[3]
        self.assertEqual(
            encode_learning_resource(resource, "Deepen fundamentals"),
            encode_learning_resource(resource, "Deepen fundamentals"),
        )

    def test_unknown_goal_uses_default_bucket(self):
        resource = LEARNING_CATALOG[1]
        self.assertEqual(
            encode_learning_resource(resource, "not a goal")[-2:],
            [0, 0],
        )

    def test_recommendation_percentage(self):
        self.assertEqual(recommendation_percentage([1, 1, 0, 0]), 50)
        self.assertEqual(recommendation_percentage([]), 0)

    def test_pick_next_learning_resource_skips_seen_titles(self):
        first = LEARNING_CATALOG[0]
        picked = pick_next_learning_resource([first.title], 0)
        self.assertNotEqual(picked.title, first.title)

    def test_format_learning_card_contains_key_fields(self):
        resource = LEARNING_CATALOG[0]
        card = format_learning_card(resource)
        self.assertIn(resource.title, card)
        self.assertIn(resource.provider, card)
        self.assertIn(str(resource.duration_minutes), card)


if __name__ == "__main__":
    unittest.main()
