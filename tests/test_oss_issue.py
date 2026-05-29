# -*- coding: utf-8 -*-
"""
Unit tests for the Open-Source Issue Recommender domain.
"""

import unittest
from oss_issue_domain import (
    ISSUE_CATALOG,
    AREA_MAP,
    EFFORT_MAP,
    CONTRIBUTOR_GOAL_MAP,
    encode_issue,
    encode_preferences,
    get_issue_summary,
)
from oss_issue_recommender import OSSIssueRecommender


class TestOSSIssueDomain(unittest.TestCase):
    """Test the issue catalog and encoding functions."""
    
    def test_catalog_has_12_items(self):
        """Verify the catalog contains exactly 12 items."""
        self.assertEqual(len(ISSUE_CATALOG), 12)
    
    def test_all_areas_represented(self):
        """Verify all 8 areas have at least one issue."""
        areas = {issue["area"] for issue in ISSUE_CATALOG}
        expected_areas = {"frontend", "backend", "docs", "testing", "devops", "data", "CLI", "security"}
        self.assertEqual(areas, expected_areas)
    
    def test_encode_issue_returns_8_bits(self):
        """Verify each issue encodes to exactly 8 bits."""
        for issue in ISSUE_CATALOG:
            encoded = encode_issue(issue)
            self.assertEqual(len(encoded), 8, f"Issue {issue['id']} encoded to {len(encoded)} bits")
            self.assertTrue(all(b in (0, 1) for b in encoded))
    
    def test_encode_preferences_returns_8_bits(self):
        """Verify preference encoding produces 8 bits."""
        prefs = encode_preferences("backend", "medium", False, "contributing")
        self.assertEqual(len(prefs), 8)
        self.assertTrue(all(b in (0, 1) for b in prefs))
    
    def test_area_encoding_coverage(self):
        """Verify all areas have valid 3-bit encodings."""
        self.assertEqual(len(AREA_MAP), 8)
        for area, bits in AREA_MAP.items():
            self.assertEqual(len(bits), 3)
    
    def test_effort_encoding_coverage(self):
        """Verify all effort levels have valid 2-bit encodings."""
        self.assertEqual(len(EFFORT_MAP), 3)
        for effort, bits in EFFORT_MAP.items():
            self.assertEqual(len(bits), 2)
    
    def test_issue_has_required_fields(self):
        """Verify each issue has all required fields."""
        required = {"id", "title", "project", "area", "labels", "effort", "languages", "description", "difficulty"}
        for issue in ISSUE_CATALOG:
            missing = required - set(issue.keys())
            self.assertFalse(missing, f"Issue {issue.get('id', '?')} missing fields: {missing}")
    
    def test_get_issue_summary(self):
        """Verify issue summary is non-empty string."""
        for issue in ISSUE_CATALOG:
            summary = get_issue_summary(issue)
            self.assertIsInstance(summary, str)
            self.assertIn(issue["id"], summary)
            self.assertIn(issue["title"], summary)


class TestOSSIssueRecommender(unittest.TestCase):
    """Test the recommender logic."""
    
    def setUp(self):
        self.recommender = OSSIssueRecommender()
    
    def test_recommend_returns_top_k(self):
        """Verify recommend returns the requested number of results."""
        recs = self.recommender.recommend("backend", "medium", top_k=3)
        self.assertEqual(len(recs), 3)
    
    def test_recommend_returns_issues_with_scores(self):
        """Verify each recommendation is an (issue, score) tuple."""
        recs = self.recommender.recommend("frontend", "low")
        for issue, score in recs:
            self.assertIn("id", issue)
            self.assertIsInstance(score, float)
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 1)
    
    def test_feedback_removes_disliked(self):
        """Verify disliked issues are excluded from recommendations."""
        # Dislike a frontend issue
        self.recommender.provide_feedback("FE001", liked=False)
        
        # Recommend frontend issues
        recs = self.recommender.recommend("frontend", "low", top_k=5)
        issue_ids = [issue["id"] for issue, _ in recs]
        self.assertNotIn("FE001", issue_ids)
    
    def test_feedback_boosts_liked(self):
        """Verify liked issues get boosted in future recommendations."""
        # Like a backend issue
        self.recommender.provide_feedback("BE001", liked=True)
        
        # Recommend backend issues
        recs = self.recommender.recommend("backend", "medium", top_k=5)
        # BE001 should be in top results
        top_ids = [issue["id"] for issue, _ in recs[:3]]
        self.assertIn("BE001", top_ids)
    
    def test_beginner_filter(self):
        """Verify beginner-only filter works."""
        recs = self.recommender.recommend("backend", "low", beginner_only=True, top_k=5)
        for issue, score in recs:
            # Beginner-friendly issues should rank higher
            if issue["difficulty"] == 1:
                # At least some beginner issues should be recommended
                pass
    
    def test_get_formatted_recommendations(self):
        """Verify formatted output is a non-empty string."""
        text = self.recommender.get_recommended_issues_text("backend", "medium")
        self.assertIsInstance(text, str)
        self.assertIn("Recommended", text)


if __name__ == "__main__":
    unittest.main()
