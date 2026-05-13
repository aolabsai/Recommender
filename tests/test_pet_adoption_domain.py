import unittest

from pet_adoption_domain import (
    encode_pet,
    get_pet_by_id,
    rank_pets,
)


class PetAdoptionDomainTest(unittest.TestCase):
    def test_encode_pet_returns_ao_compatible_eight_bit_input(self):
        pet = get_pet_by_id("ranger")

        self.assertEqual(
            encode_pet(pet, adoption_goal="active"),
            [0, 0, 1, 1, 1, 1, 0, 1],
        )

    def test_rank_pets_matches_apartment_companion_context(self):
        recommendations = rank_pets(
            preferred_species="cat",
            home_type="apartment",
            activity_level="low",
            has_children=False,
            experience_level="new",
            adoption_goal="companion",
            limit=3,
        )

        self.assertEqual(recommendations[0]["id"], "luna")
        self.assertEqual(recommendations[0]["species"], "cat")
        self.assertGreaterEqual(recommendations[0]["score"], recommendations[1]["score"])

    def test_rank_pets_matches_active_dog_context(self):
        recommendations = rank_pets(
            preferred_species="dog",
            home_type="house",
            activity_level="high",
            has_children=True,
            experience_level="experienced",
            adoption_goal="active",
            limit=3,
        )

        self.assertEqual(recommendations[0]["id"], "ranger")
        self.assertIn("hiking", recommendations[0]["traits"])

    def test_feedback_can_change_recommendation_order(self):
        baseline = rank_pets(
            preferred_species="any",
            home_type="house",
            activity_level="medium",
            has_children=True,
            experience_level="new",
            adoption_goal="family",
            limit=2,
        )

        with_feedback = rank_pets(
            preferred_species="any",
            home_type="house",
            activity_level="medium",
            has_children=True,
            experience_level="new",
            adoption_goal="family",
            feedback=[{"pet_id": "milo", "liked": True}],
            limit=2,
        )

        self.assertNotEqual(baseline[0]["id"], "milo")
        self.assertEqual(with_feedback[0]["id"], "milo")

    def test_invalid_species_is_rejected(self):
        with self.assertRaises(ValueError):
            rank_pets(preferred_species="dragon")


if __name__ == "__main__":
    unittest.main()
