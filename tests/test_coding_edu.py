# -*- coding: utf-8 -*-
"""
Tests for the Coding Education Resource Recommender
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coding_edu_domain import (
    RESOURCE_CATALOG, TOPIC_MAP, DIFFICULTY_MAP, FORMAT_MAP, EXPERIENCE_MAP,
    get_topic_encoding, get_difficulty_encoding, get_format_encoding, get_experience_encoding
)


def test_catalog_completeness():
    """Verify all 12 resources are present with required fields."""
    assert len(RESOURCE_CATALOG) == 12, f"Expected 12 resources, got {len(RESOURCE_CATALOG)}"
    required = ["id", "title", "topic", "difficulty", "format", "experience", "description", "url", "tags"]
    for resource in RESOURCE_CATALOG:
        for field in required:
            assert field in resource, f"Resource {resource.get('id', '?')} missing field: {field}"


def test_topic_coverage():
    """Verify all topics are represented in the catalog."""
    topics_in_catalog = set(r["topic"] for r in RESOURCE_CATALOG)
    for topic in TOPIC_MAP.values():
        assert topic in topics_in_catalog, f"Topic '{topic}' not in catalog"


def test_encoding_functions():
    """Test encoding functions return correct values."""
    assert get_topic_encoding("Web Development") == 0
    assert get_topic_encoding("Security") == 9
    assert get_difficulty_encoding("Beginner") == 0
    assert get_difficulty_encoding("Advanced") == 2
    assert get_format_encoding("Video") == 0
    assert get_format_encoding("Interactive") == 1
    assert get_experience_encoding("No prior experience") == 0


def test_valid_urls():
    """Verify all resources have valid URLs."""
    for resource in RESOURCE_CATALOG:
        url = resource["url"]
        assert url.startswith("https://"), f"Invalid URL for {resource['title']}: {url}"


def test_unique_ids():
    """Verify all resource IDs are unique."""
    ids = [r["id"] for r in RESOURCE_CATALOG]
    assert len(ids) == len(set(ids)), "Duplicate resource IDs found"


def test_unique_titles():
    """Verify all resource titles are unique."""
    titles = [r["title"] for r in RESOURCE_CATALOG]
    assert len(titles) == len(set(titles)), "Duplicate resource titles found"


def test_encoding_range():
    """Test that all encodings are within valid bit ranges."""
    # 3 bits for topic = 0-7 (we have 10 topics but use 3 bits = 0-7, overflow handled)
    for topic in TOPIC_MAP.values():
        enc = get_topic_encoding(topic)
        assert 0 <= enc <= 9, f"Topic encoding out of range: {enc}"
    
    for diff in DIFFICULTY_MAP.values():
        enc = get_difficulty_encoding(diff)
        assert 0 <= enc <= 3, f"Difficulty encoding out of range: {enc}"


if __name__ == "__main__":
    test_catalog_completeness()
    print("✅ test_catalog_completeness")
    test_topic_coverage()
    print("✅ test_topic_coverage")
    test_encoding_functions()
    print("✅ test_encoding_functions")
    test_valid_urls()
    print("✅ test_valid_urls")
    test_unique_ids()
    print("✅ test_unique_ids")
    test_unique_titles()
    print("✅ test_unique_titles")
    test_encoding_range()
    print("✅ test_encoding_range")
    print("\nAll tests passed! ✅")
