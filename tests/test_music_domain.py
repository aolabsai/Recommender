import unittest

from music_domain import (
    MUSIC_CATALOG,
    encode_track,
    format_track_card,
    load_catalog_from_csv,
    pick_next_track,
    recommendation_percentage,
)


class MusicDomainTests(unittest.TestCase):
    def test_catalog_titles_are_unique(self):
        titles = [track.title for track in MUSIC_CATALOG]
        self.assertEqual(len(titles), len(set(titles)))

    def test_encode_track_returns_eleven_binary_features(self):
        bits = encode_track(MUSIC_CATALOG[0], "Focus")
        self.assertEqual(len(bits), 11)
        self.assertTrue(all(bit in (0, 1) for bit in bits))

    def test_encode_track_is_deterministic(self):
        track = MUSIC_CATALOG[3]
        self.assertEqual(
            encode_track(track, "Workout"),
            encode_track(track, "Workout"),
        )

    def test_unknown_context_uses_default_bucket(self):
        track = MUSIC_CATALOG[1]
        self.assertEqual(encode_track(track, "not a context")[-2:], [0, 0])

    def test_recommendation_percentage(self):
        self.assertEqual(recommendation_percentage([1, 1, 0, 0]), 50)
        self.assertEqual(recommendation_percentage([]), 0)

    def test_pick_next_track_skips_seen_titles(self):
        first = MUSIC_CATALOG[0]
        picked = pick_next_track([first.title], 0)
        self.assertNotEqual(picked.title, first.title)

    def test_pick_next_track_accepts_custom_catalog(self):
        csv_text = """title,artist,genres,tempo_bpm,energy,release_year,vocal,summary
Test Track,Example Artist,pop;rock,101,5,2026,yes,Demo summary
Second Track,Example Artist,jazz,88,3,2025,no,Another summary
"""
        catalog = load_catalog_from_csv(csv_text)
        picked = pick_next_track([catalog[0].title], 0, catalog)
        self.assertEqual(picked.title, catalog[1].title)

    def test_load_catalog_from_csv_validates_required_columns(self):
        with self.assertRaises(ValueError):
            load_catalog_from_csv("title,artist\nMissing,Columns\n")

    def test_load_catalog_from_csv_parses_binary_features(self):
        csv_text = """title,artist,genres,tempo_bpm,energy,release_year,vocal,summary
CSV Track,CSV Artist,electronic;pop,128,8,2024,instrumental,Upload-ready record
"""
        catalog = load_catalog_from_csv(csv_text)
        self.assertEqual(catalog[0].genres, ("electronic", "pop"))
        self.assertFalse(catalog[0].vocal)
        self.assertEqual(len(encode_track(catalog[0], "Focus")), 11)

    def test_format_track_card_contains_key_fields(self):
        track = MUSIC_CATALOG[0]
        card = format_track_card(track)
        self.assertIn(track.title, card)
        self.assertIn(track.artist, card)
        self.assertIn(str(track.tempo_bpm), card)


if __name__ == "__main__":
    unittest.main()
