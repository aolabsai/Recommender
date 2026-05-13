"""Community volunteering domain helpers for the AO recommender bounty.

The module keeps the domain deterministic and dependency-free so reviewers can
exercise the recommender without private AO packages or third-party APIs.
"""

from __future__ import annotations

from dataclasses import dataclass


CATEGORY_BITS = {
    "education": [0, 0, 0],
    "environment": [0, 0, 1],
    "food_security": [0, 1, 0],
    "elder_care": [0, 1, 1],
    "animal_welfare": [1, 0, 0],
    "disaster_response": [1, 0, 1],
    "arts_culture": [1, 1, 0],
    "civic_support": [1, 1, 1],
}

TIME_BITS = {
    "short": [0, 0],
    "medium": [0, 1],
    "long": [1, 0],
    "ongoing": [1, 1],
}

SKILL_BITS = {
    "beginner": [0],
    "skilled": [1],
}

GOAL_BITS = {
    "meet_people": [0, 0],
    "use_skills": [0, 1],
    "learn": [1, 0],
    "high_impact": [1, 1],
}

GOAL_CATEGORY_PREFERENCES = {
    "meet_people": {"arts_culture", "civic_support", "food_security"},
    "use_skills": {"education", "disaster_response", "civic_support"},
    "learn": {"environment", "animal_welfare", "education"},
    "high_impact": {"food_security", "elder_care", "disaster_response"},
}

TIME_ORDER = {"short": 0, "medium": 1, "long": 2, "ongoing": 3}


@dataclass(frozen=True)
class VolunteerOpportunity:
    name: str
    category: str
    time_commitment: str
    skill_level: str
    setting: str
    impact: str
    description: str


VOLUNTEER_CATALOG = [
    VolunteerOpportunity(
        "Weekend Food Pantry Sort",
        "food_security",
        "short",
        "beginner",
        "in_person",
        "high",
        "Sort donated food and prepare pickup boxes for families.",
    ),
    VolunteerOpportunity(
        "After-School Math Tutor",
        "education",
        "ongoing",
        "skilled",
        "hybrid",
        "high",
        "Tutor middle-school learners for one hour each week.",
    ),
    VolunteerOpportunity(
        "Neighborhood Tree Mapping",
        "environment",
        "medium",
        "beginner",
        "outdoor",
        "medium",
        "Map shade trees and record maintenance needs for a local group.",
    ),
    VolunteerOpportunity(
        "Senior Tech Help Desk",
        "elder_care",
        "medium",
        "skilled",
        "in_person",
        "high",
        "Help older adults set up phones, passwords, and video calls.",
    ),
    VolunteerOpportunity(
        "Shelter Enrichment Walks",
        "animal_welfare",
        "short",
        "beginner",
        "outdoor",
        "medium",
        "Walk adoptable dogs and record behavior notes for shelter staff.",
    ),
    VolunteerOpportunity(
        "Emergency Supply Kit Build",
        "disaster_response",
        "long",
        "beginner",
        "in_person",
        "high",
        "Pack emergency kits for flood and typhoon preparedness drives.",
    ),
    VolunteerOpportunity(
        "Community Mural Assistant",
        "arts_culture",
        "medium",
        "beginner",
        "in_person",
        "medium",
        "Support artists with setup, paint stations, and visitor guidance.",
    ),
    VolunteerOpportunity(
        "Open Data Cleanup Sprint",
        "civic_support",
        "medium",
        "skilled",
        "remote",
        "high",
        "Clean public-service datasets for a civic technology project.",
    ),
    VolunteerOpportunity(
        "Beach Microplastic Survey",
        "environment",
        "short",
        "beginner",
        "outdoor",
        "medium",
        "Collect and tag microplastic samples for a coastal cleanup team.",
    ),
    VolunteerOpportunity(
        "Resume Clinic Reviewer",
        "civic_support",
        "short",
        "skilled",
        "remote",
        "medium",
        "Review resumes for job seekers served by a nonprofit partner.",
    ),
    VolunteerOpportunity(
        "Community Kitchen Prep Lead",
        "food_security",
        "long",
        "skilled",
        "in_person",
        "high",
        "Lead safe prep stations for a weekly community meal service.",
    ),
    VolunteerOpportunity(
        "Library Story Hour Helper",
        "education",
        "short",
        "beginner",
        "in_person",
        "medium",
        "Prepare reading materials and guide kids through activity stations.",
    ),
]


def encode_opportunity(opportunity: VolunteerOpportunity, user_goal: str) -> list[int]:
    """Encode an opportunity plus user goal into the 8-bit AO input shape."""
    if opportunity.category not in CATEGORY_BITS:
        raise ValueError(f"unknown category: {opportunity.category}")
    if opportunity.time_commitment not in TIME_BITS:
        raise ValueError(f"unknown time commitment: {opportunity.time_commitment}")
    if opportunity.skill_level not in SKILL_BITS:
        raise ValueError(f"unknown skill level: {opportunity.skill_level}")
    if user_goal not in GOAL_BITS:
        raise ValueError(f"unknown user goal: {user_goal}")

    return (
        CATEGORY_BITS[opportunity.category]
        + TIME_BITS[opportunity.time_commitment]
        + SKILL_BITS[opportunity.skill_level]
        + GOAL_BITS[user_goal]
    )


def score_opportunity(
    opportunity: VolunteerOpportunity,
    user_goal: str,
    max_time: str = "ongoing",
    skilled_ok: bool = True,
    feedback: dict[str, int] | None = None,
) -> int:
    """Rank opportunities with deterministic local logic for fallback mode."""
    if user_goal not in GOAL_BITS:
        raise ValueError(f"unknown user goal: {user_goal}")
    if max_time not in TIME_BITS:
        raise ValueError(f"unknown max time: {max_time}")

    score = 0
    if opportunity.category in GOAL_CATEGORY_PREFERENCES[user_goal]:
        score += 4
    if opportunity.impact == "high":
        score += 2
    if TIME_ORDER[opportunity.time_commitment] <= TIME_ORDER[max_time]:
        score += 2
    else:
        score -= 3
    if opportunity.skill_level == "beginner" or skilled_ok:
        score += 1
    else:
        score -= 2
    if feedback:
        score += feedback.get(opportunity.category, 0)
    return score


def recommend_opportunities(
    user_goal: str,
    max_time: str = "ongoing",
    skilled_ok: bool = True,
    feedback: dict[str, int] | None = None,
    limit: int = 3,
) -> list[VolunteerOpportunity]:
    """Return the top local volunteering recommendations."""
    ranked = sorted(
        VOLUNTEER_CATALOG,
        key=lambda item: (
            score_opportunity(item, user_goal, max_time, skilled_ok, feedback),
            -TIME_ORDER[item.time_commitment],
            item.name,
        ),
        reverse=True,
    )
    return ranked[:limit]

