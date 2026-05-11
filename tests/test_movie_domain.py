import unittest

from movie_domain import (
    MOVIE_CATALOG,
    encode_movie,
    format_movie_card,
    pick_next_movie,
    recommendation_percentage,
)


class MovieDomainTests(unittest.TestCase):
    def test_catalog_titles_are_unique(self):
        titles = [movie.title for movie in MOVIE_CATALOG]
        self.assertEqual(len(titles), len(set(titles)))

    def test_encode_movie_returns_nine_binary_features(self):
        bits = encode_movie(MOVIE_CATALOG[0], "Focused")
        self.assertEqual(len(bits), 9)
        self.assertTrue(all(bit in (0, 1) for bit in bits))

    def test_encode_movie_is_deterministic(self):
        movie = MOVIE_CATALOG[3]
        self.assertEqual(
            encode_movie(movie, "Easy watch"),
            encode_movie(movie, "Easy watch"),
        )

    def test_unknown_mood_uses_default_bucket(self):
        movie = MOVIE_CATALOG[1]
        self.assertEqual(encode_movie(movie, "not a mood")[-2:], [0, 0])

    def test_recommendation_percentage(self):
        self.assertEqual(recommendation_percentage([1, 1, 0, 0]), 50)
        self.assertEqual(recommendation_percentage([]), 0)

    def test_pick_next_movie_skips_seen_titles(self):
        first = MOVIE_CATALOG[0]
        picked = pick_next_movie([first.title], 0)
        self.assertNotEqual(picked.title, first.title)

    def test_format_movie_card_contains_key_fields(self):
        movie = MOVIE_CATALOG[0]
        card = format_movie_card(movie)
        self.assertIn(movie.title, card)
        self.assertIn(str(movie.year), card)
        self.assertIn(str(movie.runtime_minutes), card)


if __name__ == "__main__":
    unittest.main()
