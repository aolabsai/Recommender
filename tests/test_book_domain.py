import unittest

from book_domain import BOOK_CATALOG, binary_input_size, encode_book, recommend_books


class BookDomainTests(unittest.TestCase):
    def test_encoding_has_stable_binary_shape(self):
        encoded = encode_book(BOOK_CATALOG[0], mood="curious")

        self.assertEqual(len(encoded), binary_input_size())
        self.assertTrue(all(bit in (0, 1) for bit in encoded))

    def test_recommendation_prioritizes_matching_context(self):
        results = recommend_books(
            {
                "genre": "fantasy",
                "pace": "gentle",
                "length": "short",
                "tone": "cozy",
                "format": "novel",
                "mood": "comfort",
            },
            limit=1,
        )

        self.assertEqual(results[0]["id"], "legends-and-lattes")

    def test_recommendation_supports_nonfiction_focus(self):
        results = recommend_books(
            {
                "genre": "productivity",
                "pace": "medium",
                "length": "medium",
                "tone": "practical",
                "format": "nonfiction",
                "mood": "focused",
            },
            limit=2,
        )

        self.assertEqual(results[0]["id"], "deep-work")
        self.assertTrue(all(book["format"] == "nonfiction" for book in results))


if __name__ == "__main__":
    unittest.main()
