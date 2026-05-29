# -*- coding: utf-8 -*-
"""
Open-Source Issue Recommender
Main recommender logic for suggesting open-source issues to contributors.

Uses AO architecture to match contributor preferences with issue characteristics.
"""

import numpy as np
from oss_issue_domain import (
    ISSUE_CATALOG,
    encode_issue,
    encode_preferences,
    get_issue_summary,
)

try:
    import ao_core as ao
    from arch__Recommender import arch
    HAS_AO = True
except ImportError:
    HAS_AO = False


class OSSIssueRecommender:
    """Recommends open-source GitHub issues based on contributor preferences.
    
    Uses the AO framework to learn from feedback (liked/disliked issues)
    and improve future recommendations.
    """
    
    def __init__(self):
        self.catalog = ISSUE_CATALOG
        self.encoded_issues = [encode_issue(issue) for issue in self.catalog]
        self.feedback_history = []  # (issue_index, liked: bool)
        self.liked_indices = set()
        self.disliked_indices = set()
        
        if HAS_AO:
            self.agent = ao.Agent(arch, notes="OSS Issue Recommender")
            # Pre-train agent
            for _ in range(4):
                self.agent.reset_state()
                self.agent.reset_state(training=True)
        else:
            self.agent = None
    
    def recommend(self, preferred_area="backend", preferred_effort="medium",
                  beginner_only=False, goal="learning", top_k=3):
        """Recommend issues matching contributor preferences.
        
        Args:
            preferred_area: Area of interest (frontend/backend/docs/testing/devops/data/CLI/security)
            preferred_effort: Effort level (low/medium/high)
            beginner_only: Filter for beginner-friendly issues only
            goal: Contributor goal (learning/contributing/maintaining)
            top_k: Number of recommendations to return
            
        Returns:
            List of (issue, score) tuples sorted by relevance
        """
        prefs = encode_preferences(preferred_area, preferred_effort, beginner_only, goal)
        
        scored_issues = []
        for idx, (issue, encoded) in enumerate(zip(self.catalog, self.encoded_issues)):
            # Skip disliked issues
            if idx in self.disliked_indices:
                continue
            
            # Calculate match score based on preference overlap
            score = self._calculate_score(prefs, encoded, idx)
            scored_issues.append((issue, score))
        
        # Sort by score descending
        scored_issues.sort(key=lambda x: x[1], reverse=True)
        return scored_issues[:top_k]
    
    def _calculate_score(self, preferences, encoded_issue, issue_idx):
        """Calculate match score between preferences and issue.
        
        Combines bit-overlap similarity with feedback-based adjustments.
        """
        # Bit overlap score
        matches = sum(1 for p, i in zip(preferences, encoded_issue) if p == i and p == 1)
        total_bits = sum(1 for p in preferences if p == 1)
        
        if total_bits == 0:
            base_score = 0.5
        else:
            base_score = matches / total_bits
        
        # Boost score for liked-similar issues
        boost = 0.0
        for liked_idx in self.liked_indices:
            liked_encoded = self.encoded_issues[liked_idx]
            similarity = sum(1 for a, b in zip(liked_encoded, encoded_issue) if a == b) / 8
            boost += similarity * 0.1
        
        # Penalize if similar to disliked issues
        penalty = 0.0
        for disliked_idx in self.disliked_indices:
            disliked_encoded = self.encoded_issues[disliked_idx]
            similarity = sum(1 for a, b in zip(disliked_encoded, encoded_issue) if a == b) / 8
            penalty += similarity * 0.15
        
        return max(0, min(1, base_score + boost - penalty))
    
    def provide_feedback(self, issue_id, liked):
        """Provide feedback on a recommended issue.
        
        Args:
            issue_id: The issue ID (e.g., "FE001")
            liked: True if the contributor likes this recommendation
        """
        for idx, issue in enumerate(self.catalog):
            if issue["id"] == issue_id:
                if liked:
                    self.liked_indices.add(idx)
                    self.disliked_indices.discard(idx)
                else:
                    self.disliked_indices.add(idx)
                    self.liked_indices.discard(idx)
                self.feedback_history.append((idx, liked))
                
                # Update AO agent if available
                if self.agent:
                    self._update_agent(idx, liked)
                break
    
    def _update_agent(self, issue_idx, liked):
        """Update the AO agent with feedback."""
        encoded = self.encoded_issues[issue_idx]
        try:
            z = encoded
            self.agent.step(z, learning_enabled=True, reward=1 if liked else -1)
        except Exception:
            pass  # AO agent update is optional
    
    def get_recommended_issues_text(self, preferred_area="backend", preferred_effort="medium",
                                     beginner_only=False, goal="learning", top_k=3):
        """Get formatted text of recommended issues."""
        recs = self.recommend(preferred_area, preferred_effort, beginner_only, goal, top_k)
        if not recs:
            return "No matching issues found. Try adjusting your preferences."
        
        lines = ["=== Recommended Open-Source Issues ===\n"]
        for i, (issue, score) in enumerate(recs, 1):
            lines.append(f"{i}. {get_issue_summary(issue)}")
            lines.append(f"  Match Score: {score:.1%}\n")
        return "\n".join(lines)


def cli_mode():
    """Command-line interface for the recommender."""
    recommender = OSSIssueRecommender()
    
    print("=== Open-Source Issue Recommender ===")
    print("Find the perfect open-source issue to work on!\n")
    
    # Get preferences
    print("Available areas: frontend, backend, docs, testing, devops, data, CLI, security")
    area = input("Preferred area (default: backend): ").strip() or "backend"
    
    print("\nEffort levels: low, medium, high")
    effort = input("Preferred effort (default: medium): ").strip() or "medium"
    
    beginner = input("Only beginner-friendly issues? (y/n, default: n): ").strip().lower() == "y"
    
    print("\nGoals: learning, contributing, maintaining")
    goal = input("Your goal (default: learning): ").strip() or "learning"
    
    # Get recommendations
    print("\n" + recommender.get_recommended_issues_text(
        preferred_area=area,
        preferred_effort=effort,
        beginner_only=beginner,
        goal=goal,
        top_k=5
    ))
    
    # Feedback loop
    while True:
        feedback = input("\nLike an issue? Enter ID to like, '-ID' to dislike, or 'q' to quit: ").strip()
        if feedback.lower() == "q":
            break
        
        if feedback.startswith("-"):
            recommender.provide_feedback(feedback[1:].upper(), liked=False)
        elif feedback:
            recommender.provide_feedback(feedback.upper(), liked=True)
        
        # Show updated recommendations
        print("\n" + recommender.get_recommended_issues_text(area, effort, beginner, goal, 5))


if __name__ == "__main__":
    cli_mode()
