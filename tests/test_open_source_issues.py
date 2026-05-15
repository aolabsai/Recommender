import unittest

from open_source_issues import ISSUE_CATALOG, encode_issue, recommend_issues, score_issue


class OpenSourceIssueRecommenderTest(unittest.TestCase):
    def test_encoding_matches_architecture_shape(self):
        encoding = encode_issue(ISSUE_CATALOG[0], "quick-win")
        self.assertEqual(len(encoding), 8)
        self.assertTrue(all(bit in {0, 1} for bit in encoding))

    def test_quick_win_prefers_short_beginner_tasks(self):
        docs_task = next(task for task in ISSUE_CATALOG if task.title.startswith("Document OAuth"))
        security_task = next(task for task in ISSUE_CATALOG if task.title.startswith("Harden archive"))

        docs_score = score_issue(docs_task, {"docs"}, "quick-win", max_minutes=45)
        security_score = score_issue(security_task, {"security"}, "quick-win", max_minutes=45)

        self.assertGreater(docs_score, security_score)

    def test_recommendations_return_ranked_payloads(self):
        results = recommend_issues({"tests", "security"}, "maintainer", max_minutes=90, limit=3)

        self.assertEqual(len(results), 3)
        self.assertGreaterEqual(results[0]["score"], results[1]["score"])
        self.assertIn("encoding", results[0])
        self.assertEqual(len(results[0]["encoding"]), 8)


if __name__ == "__main__":
    unittest.main()
