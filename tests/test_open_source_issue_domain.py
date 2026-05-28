import unittest

from open_source_issue_domain import (
    encode_issue,
    get_issue_by_id,
    rank_issues,
)


class OpenSourceIssueDomainTest(unittest.TestCase):
    def test_encode_issue_returns_ao_compatible_eight_bit_input(self):
        issue = get_issue_by_id("api-pagination-bounds")

        self.assertEqual(
            encode_issue(issue, goal="maintainer-impact"),
            [0, 0, 1, 0, 0, 1, 1, 1],
        )

    def test_rank_issues_matches_new_frontend_contributor(self):
        recommendations = rank_issues(
            preferred_area="frontend",
            effort_budget="small",
            contributor_level="new",
            wants_beginner_friendly=True,
            goal="portfolio",
            stack=["react", "css"],
            limit=3,
        )

        self.assertEqual(recommendations[0]["id"], "keyboard-navigation-audit")
        self.assertEqual(recommendations[0]["area"], "frontend")
        self.assertGreaterEqual(recommendations[0]["score"], recommendations[1]["score"])

    def test_rank_issues_matches_devops_maintainer_goal(self):
        recommendations = rank_issues(
            preferred_area="devops",
            effort_budget="medium",
            contributor_level="experienced",
            goal="maintainer-impact",
            stack=["docker", "ci"],
            limit=3,
        )

        self.assertEqual(recommendations[0]["id"], "ci-cache-split")
        self.assertEqual(recommendations[0]["area"], "devops")

    def test_feedback_can_change_recommendation_order(self):
        baseline = rank_issues(
            preferred_area="any",
            effort_budget="medium",
            contributor_level="intermediate",
            goal="quick-win",
            stack=["python"],
            limit=2,
        )

        with_feedback = rank_issues(
            preferred_area="any",
            effort_budget="medium",
            contributor_level="intermediate",
            goal="quick-win",
            stack=["python"],
            feedback=[{"issue_id": "csv-import-memory", "liked": True}],
            limit=2,
        )

        self.assertNotEqual(baseline[0]["id"], "csv-import-memory")
        self.assertEqual(with_feedback[0]["id"], "csv-import-memory")

    def test_invalid_area_is_rejected(self):
        with self.assertRaises(ValueError):
            rank_issues(preferred_area="mobile")


if __name__ == "__main__":
    unittest.main()
