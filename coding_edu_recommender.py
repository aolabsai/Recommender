# -*- coding: utf-8 -*-
"""
Programming Education Resource Recommender
A Streamlit-based recommender that suggests coding tutorials, courses, 
and practice resources based on user preferences and learning progress.

Uses AO Labs' architecture for post-training learning.
"""

import streamlit as st
import numpy as np
import random

from coding_edu_domain import (
    RESOURCE_CATALOG, TOPIC_MAP, DIFFICULTY_MAP, FORMAT_MAP, EXPERIENCE_MAP,
    get_topic_encoding, get_difficulty_encoding, get_format_encoding, get_experience_encoding
)

try:
    import ao_core as ao
    from arch__CodingEduRecommender import arch
    HAS_AO = True
except ImportError:
    HAS_AO = False
    print("Warning: ao_core not available, running in demo mode")

def init_session_state():
    """Initialize all session state variables."""
    if "edu_resources_seen" not in st.session_state:
        st.session_state.edu_resources_seen = []
    if "edu_recommendation_result" not in st.session_state:
        st.session_state.edu_recommendation_result = None
    if "edu_training_history" not in st.session_state:
        st.session_state.edu_training_history = np.zeros([1000, 7], dtype="O")
    if "edu_agent" not in st.session_state:
        if HAS_AO:
            st.session_state.edu_agent = ao.Agent(arch, notes="Coding Edu Recommender")
            for i in range(4):
                st.session_state.edu_agent.reset_state()
                st.session_state.edu_agent.reset_state(training=True)
        else:
            st.session_state.edu_agent = None
    if "edu_recommended" not in st.session_state:
        st.session_state.edu_recommended = False
    if "edu_topic" not in st.session_state:
        st.session_state.edu_topic = "Web Development"
    if "edu_difficulty" not in st.session_state:
        st.session_state.edu_difficulty = "Beginner"
    if "edu_format" not in st.session_state:
        st.session_state.edu_format = "Interactive"
    if "edu_experience" not in st.session_state:
        st.session_state.edu_experience = "No prior experience"


def encode_user_input(topic, difficulty, fmt, experience):
    """Encode user preferences into binary input for AO architecture."""
    topic_enc = format(get_topic_encoding(topic), f'03b')
    diff_enc = format(get_difficulty_encoding(difficulty), f'02b')
    fmt_enc = format(get_format_encoding(fmt), f'01b')
    exp_enc = format(get_experience_encoding(experience), f'02b')
    
    binary_str = topic_enc + diff_enc + fmt_enc + exp_enc
    return [int(b) for b in binary_str]


def get_resource_recommendation(topic, difficulty, fmt, experience):
    """Get a resource recommendation based on user preferences."""
    # Filter resources matching preferences
    candidates = []
    for resource in RESOURCE_CATALOG:
        score = 0
        if resource["topic"] == topic:
            score += 4
        if resource["difficulty"] == difficulty:
            score += 3
        if resource["format"] == fmt:
            score += 2
        if resource["experience"] == experience:
            score += 2
        # Penalize already seen resources
        if resource["id"] in st.session_state.edu_resources_seen:
            score -= 5
        candidates.append((resource, score))
    
    # Sort by score and add some randomness
    candidates.sort(key=lambda x: x[1] + random.uniform(0, 1.5), reverse=True)
    
    if candidates and candidates[0][1] > 0:
        best = candidates[0][0]
        st.session_state.edu_resources_seen.append(best["id"])
        return best
    
    # Fallback: random unseen resource
    unseen = [r for r in RESOURCE_CATALOG if r["id"] not in st.session_state.edu_resources_seen]
    if unseen:
        chosen = random.choice(unseen)
        st.session_state.edu_resources_seen.append(chosen["id"])
        return chosen
    
    # All seen, reset
    st.session_state.edu_resources_seen = []
    return random.choice(RESOURCE_CATALOG)


def train_on_feedback(resource, liked):
    """Train the agent based on user feedback."""
    if st.session_state.edu_agent is None:
        return
    
    binary_input = encode_user_input(
        resource["topic"], resource["difficulty"],
        resource["format"], resource["experience"]
    )
    
    # Positive feedback = reinforce, negative = discourage
    reward = 1 if liked else -1
    
    idx = st.session_state.get("edu_num_trained", 0)
    st.session_state.edu_training_history[idx] = [
        resource["id"], binary_input, reward, liked,
        resource["topic"], resource["difficulty"], resource["format"]
    ]
    st.session_state.edu_num_trained = idx + 1


def run_coding_edu_recommender():
    """Main Streamlit app for the coding education recommender."""
    st.set_page_config(page_title="Coding Edu Recommender", page_icon="📚", layout="wide")
    
    init_session_state()
    
    st.title("📚 Programming Education Recommender")
    st.markdown("*Get personalized coding tutorial recommendations that learn from your feedback!*")
    st.markdown("---")
    
    # Sidebar for preferences
    with st.sidebar:
        st.header("🎯 Your Preferences")
        
        topic = st.selectbox(
            "Programming Topic",
            list(TOPIC_MAP.values()),
            index=list(TOPIC_MAP.values()).index(st.session_state.edu_topic),
            key="edu_topic_select"
        )
        st.session_state.edu_topic = topic
        
        difficulty = st.selectbox(
            "Difficulty Level",
            list(DIFFICULTY_MAP.values())[:-1],  # Exclude Expert from selection
            index=list(DIFFICULTY_MAP.values())[:-1].index(st.session_state.edu_difficulty) if st.session_state.edu_difficulty in list(DIFFICULTY_MAP.values())[:-1] else 0,
            key="edu_difficulty_select"
        )
        st.session_state.edu_difficulty = difficulty
        
        fmt = st.selectbox(
            "Learning Format",
            list(FORMAT_MAP.values()),
            key="edu_format_select"
        )
        st.session_state.edu_format = fmt
        
        experience = st.selectbox(
            "Your Experience",
            list(EXPERIENCE_MAP.values())[:-1],
            key="edu_experience_select"
        )
        st.session_state.edu_experience = experience
        
        st.markdown("---")
        st.markdown(f"**Resources seen:** {len(st.session_state.edu_resources_seen)}/{len(RESOURCE_CATALOG)}")
        
        if st.button("🔄 Reset History"):
            st.session_state.edu_resources_seen = []
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("🎲 Get Recommendation", type="primary", use_container_width=True):
            resource = get_resource_recommendation(topic, difficulty, fmt, experience)
            st.session_state.edu_recommendation_result = resource
            st.session_state.edu_recommended = True
        
        if st.session_state.edu_recommendation_result:
            resource = st.session_state.edu_recommendation_result
            
            st.markdown(f"### 📖 {resource['title']}")
            st.markdown(f"*{resource['description']}*")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Topic", resource["topic"])
            with col_b:
                st.metric("Difficulty", resource["difficulty"])
            with col_c:
                st.metric("Format", resource["format"])
            
            st.markdown(f"**⏱ Duration:** {resource['duration']}")
            st.markdown(f"**🔗 [Start Learning]({resource['url']})**")
            st.markdown(f"**Tags:** {', '.join(resource['tags'])}")
            
            st.markdown("---")
            st.markdown("### Was this recommendation helpful?")
            
            fb_col1, fb_col2 = st.columns(2)
            with fb_col1:
                if st.button("👍 Yes, helpful!", key="edu_like"):
                    train_on_feedback(resource, True)
                    st.success("Thanks for the feedback! Training updated. 🎉")
            with fb_col2:
                if st.button("👎 Not for me", key="edu_dislike"):
                    train_on_feedback(resource, False)
                    st.info("Noted! I'll learn from this. Try another recommendation!")
    
    with col2:
        st.markdown("### 📊 Binary Encoding")
        binary = encode_user_input(
            st.session_state.edu_topic,
            st.session_state.edu_difficulty,
            st.session_state.edu_format,
            st.session_state.edu_experience
        )
        st.code(f"Input: {binary}")
        st.caption(f"Topic({binary[0:3]}) Diff({binary[3:5]}) Fmt({binary[5]}) Exp({binary[6:8]})")
        
        st.markdown("---")
        st.markdown("### 📋 All Resources")
        for r in RESOURCE_CATALOG:
            seen = "✅" if r["id"] in st.session_state.edu_resources_seen else "⬜"
            st.markdown(f"{seen} **{r['title']}** ({r['difficulty']})")


if __name__ == "__main__":
    run_coding_edu_recommender()
