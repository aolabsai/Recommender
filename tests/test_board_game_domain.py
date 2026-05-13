import unittest

from board_game_domain import (
    BOARD_GAME_CATALOG,
    encode_game,
    recommend_games,
    score_game,
)


class BoardGameDomainTest(unittest.TestCase):
    def test_encoding_keeps_ao_input_shape(self):
        game = next(item for item in BOARD_GAME_CATALOG if item.title == "Codenames")
        bits = encode_game(game, {"players": 6, "mood": "social", "available_minutes": 45})

        self.assertEqual(len(bits), 8)
        self.assertTrue(all(bit in (0, 1) for bit in bits))

    def test_player_count_filters_unplayable_games(self):
        results = recommend_games({"players": 8, "available_minutes": 90, "mood": "social"})
        titles = {item["title"] for item in results}

        self.assertIn("Codenames", titles)
        self.assertNotIn("Splendor Duel", titles)

    def test_duration_filters_long_games(self):
        results = recommend_games(
            {"players": 4, "available_minutes": 45, "mood": "casual"},
            limit=20,
        )
        titles = {item["title"] for item in results}

        self.assertIn("Azul", titles)
        self.assertNotIn("Root", titles)
        self.assertNotIn("Dune: Imperium", titles)

    def test_feedback_changes_ranking(self):
        context = {
            "players": 4,
            "available_minutes": 90,
            "mood": "social",
            "preferred_type": "party",
        }
        no_feedback = recommend_games(context, limit=3)
        with_feedback = recommend_games(
            context,
            limit=3,
            feedback=[{"title": "Just One", "game_type": "party", "mood": "social", "liked": True}],
        )

        self.assertNotEqual(no_feedback[0]["title"], with_feedback[0]["title"])
        self.assertEqual(with_feedback[0]["title"], "Just One")

    def test_invalid_player_count_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend_games({"players": 0, "available_minutes": 60})

    def test_score_marks_unplayable_games_low(self):
        duel = next(item for item in BOARD_GAME_CATALOG if item.title == "Splendor Duel")
        self.assertLess(score_game(duel, {"players": 4, "available_minutes": 60}), -99)


if __name__ == "__main__":
    unittest.main()
