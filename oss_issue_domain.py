# -*- coding: utf-8 -*-
"""
Open-Source Issue Recommender Domain
Recommends open-source GitHub issues to contributors based on their skills,
interests, and experience level.

Implements a distinct issue recommendation domain for aolabsai/ao_pyth#9.
"""

# 12-item open-source issue catalog covering diverse project areas
ISSUE_CATALOG = [
    # Frontend issues
    {
        "id": "FE001",
        "title": "Fix responsive layout on dashboard page",
        "project": "web-framework",
        "area": "frontend",
        "labels": ["bug", "good first issue", "UI"],
        "effort": "low",
        "languages": ["JavaScript", "CSS"],
        "description": "Dashboard layout breaks on mobile viewports below 768px",
        "difficulty": 1,  # 1=beginner, 2=intermediate, 3=advanced
    },
    {
        "id": "FE002",
        "title": "Implement dark mode toggle with CSS variables",
        "project": "web-framework",
        "area": "frontend",
        "labels": ["feature", "enhancement"],
        "effort": "medium",
        "languages": ["JavaScript", "CSS"],
        "description": "Add system-preference-aware dark mode with manual override",
        "difficulty": 2,
    },
    # Backend issues
    {
        "id": "BE001",
        "title": "Add pagination to REST API endpoints",
        "project": "api-server",
        "area": "backend",
        "labels": ["feature", "performance"],
        "effort": "medium",
        "languages": ["Python", "SQL"],
        "description": "Implement cursor-based pagination for list endpoints returning >100 items",
        "difficulty": 2,
    },
    {
        "id": "BE002",
        "title": "Implement rate limiting middleware",
        "project": "api-server",
        "area": "backend",
        "labels": ["feature", "security"],
        "effort": "high",
        "languages": ["Python", "Redis"],
        "description": "Add configurable per-user and per-IP rate limiting with sliding window",
        "difficulty": 3,
    },
    # Documentation issues
    {
        "id": "DC001",
        "title": "Write getting started tutorial for new contributors",
        "project": "docs-site",
        "area": "docs",
        "labels": ["documentation", "good first issue"],
        "effort": "low",
        "languages": ["Markdown"],
        "description": "Create a step-by-step tutorial for setting up the dev environment",
        "difficulty": 1,
    },
    {
        "id": "DC002",
        "title": "Add API reference documentation for v2 endpoints",
        "project": "docs-site",
        "area": "docs",
        "labels": ["documentation"],
        "effort": "medium",
        "languages": ["Markdown", "Python"],
        "description": "Document all new v2 REST API endpoints with request/response examples",
        "difficulty": 1,
    },
    # Testing issues
    {
        "id": "TS001",
        "title": "Add unit tests for authentication module",
        "project": "auth-service",
        "area": "testing",
        "labels": ["testing", "good first issue"],
        "effort": "medium",
        "languages": ["Python", "pytest"],
        "description": "Increase test coverage for login, signup, and token refresh flows",
        "difficulty": 1,
    },
    {
        "id": "TS002",
        "title": "Set up integration tests for CI pipeline",
        "project": "devops-tools",
        "area": "testing",
        "labels": ["testing", "CI/CD"],
        "effort": "high",
        "languages": ["Python", "YAML", "Docker"],
        "description": "Create end-to-end integration tests that run in GitHub Actions",
        "difficulty": 2,
    },
    # DevOps issues
    {
        "id": "DO001",
        "title": "Dockerize the application with multi-stage build",
        "project": "devops-tools",
        "area": "devops",
        "labels": ["DevOps", "Docker", "enhancement"],
        "effort": "medium",
        "languages": ["Dockerfile", "YAML"],
        "description": "Optimize Docker image size with multi-stage builds and layer caching",
        "difficulty": 2,
    },
    # Data issues
    {
        "id": "DT001",
        "title": "Create data migration script for schema v3",
        "project": "data-pipeline",
        "area": "data",
        "labels": ["data", "database", "migration"],
        "effort": "high",
        "languages": ["Python", "SQL"],
        "description": "Write migration script to convert v2 database schema to v3 with zero downtime",
        "difficulty": 3,
    },
    # CLI issues
    {
        "id": "CL001",
        "title": "Add shell completion for bash and zsh",
        "project": "cli-tool",
        "area": "CLI",
        "labels": ["CLI", "enhancement", "good first issue"],
        "effort": "low",
        "languages": ["Python", "Shell"],
        "description": "Generate shell completion scripts for all CLI commands and flags",
        "difficulty": 1,
    },
    # Security issues
    {
        "id": "SC001",
        "title": "Audit and update dependency versions for CVE fixes",
        "project": "security-scanner",
        "area": "security",
        "labels": ["security", "dependencies"],
        "effort": "medium",
        "languages": ["Python", "YAML"],
        "description": "Review all dependencies for known vulnerabilities and update to patched versions",
        "difficulty": 2,
    },
]

# Area encoding for 8-bit input
# Bits: [area(3)] [effort(2)] [beginner_friendly(1)] [contributor_goal(2)]
AREA_MAP = {
    "frontend":  [1, 0, 0],
    "backend":   [0, 1, 0],
    "docs":      [0, 0, 1],
    "testing":   [1, 1, 0],
    "devops":    [0, 1, 1],
    "data":      [1, 0, 1],
    "CLI":       [1, 1, 1],
    "security":  [0, 0, 0],
}

EFFORT_MAP = {
    "low":    [1, 0],
    "medium": [0, 1],
    "high":   [1, 1],
}

CONTRIBUTOR_GOAL_MAP = {
    "learning":  [1, 0],
    "contributing": [0, 1],
    "maintaining":  [1, 1],
}


def encode_issue(issue):
    """Encode an issue into 8-bit binary representation for AO input.
    
    Bit layout: [area(3)] [effort(2)] [beginner_friendly(1)] [difficulty_category(2)]
    """
    area_bits = AREA_MAP.get(issue["area"], [0, 0, 0])
    effort_bits = EFFORT_MAP.get(issue["effort"], [0, 0])
    beginner_bit = [1] if issue["difficulty"] == 1 else [0]
    diff_cat = CONTRIBUTOR_GOAL_MAP.get(
        "learning" if issue["difficulty"] == 1 else
        "contributing" if issue["difficulty"] == 2 else
        "maintaining", [0, 0]
    )
    return area_bits + effort_bits + beginner_bit + diff_cat


def encode_preferences(preferred_area, preferred_effort, beginner_only=False, goal="learning"):
    """Encode contributor preferences into 8-bit input.
    
    Args:
        preferred_area: Preferred issue area (e.g., "frontend", "backend")
        preferred_effort: Preferred effort level ("low", "medium", "high")
        beginner_only: Whether to filter for beginner-friendly issues only
        goal: Contributor goal ("learning", "contributing", "maintaining")
    """
    area_bits = AREA_MAP.get(preferred_area, [0, 0, 0])
    effort_bits = EFFORT_MAP.get(preferred_effort, [0, 0])
    beginner_bit = [1] if beginner_only else [0]
    goal_bits = CONTRIBUTOR_GOAL_MAP.get(goal, [0, 0])
    return area_bits + effort_bits + beginner_bit + goal_bits


def get_issue_summary(issue):
    """Get a human-readable summary of an issue."""
    return (
        f"[{issue['id']}] {issue['title']}\n"
        f"  Project: {issue['project']} | Area: {issue['area']} | "
        f"Effort: {issue['effort']} | Difficulty: {'★' * issue['difficulty']}\n"
        f"  Languages: {', '.join(issue['languages'])}\n"
        f"  {issue['description']}\n"
        f"  Labels: {', '.join(issue['labels'])}"
    )
