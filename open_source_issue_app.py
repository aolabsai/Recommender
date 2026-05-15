import numpy as np
import streamlit as st

from open_source_issues import TRACK_BITS, recommend_issues


try:
    import ao_core as ao
    from arch__OpenSourceIssueRecommender import arch
except Exception:
    ao = None
    arch = None


st.set_page_config(
    page_title="Open-Source Issue Recommender",
    page_icon="misc/ao_favicon.png",
    layout="wide",
)

if "issue_agent" not in st.session_state and ao is not None and arch is not None:
    st.session_state.issue_agent = ao.Agent(arch, notes="Open-source issue recommender")
    for _ in range(4):
        st.session_state.issue_agent.reset_state()
        st.session_state.issue_agent.reset_state(training=True)


def agent_score(binary_input: list[int]) -> float | None:
    agent = st.session_state.get("issue_agent")
    if agent is None:
        return None
    agent.reset_state()
    response = None
    for _ in range(5):
        response = agent.next_state(INPUT=binary_input, print_result=False)
    if response is None:
        return None
    return round(100 * sum(response) / len(response), 2)


def train_current(label_value: int):
    agent = st.session_state.get("issue_agent")
    current = st.session_state.get("current_issue_encoding")
    if agent is None or current is None:
        return
    label = np.full(agent.arch.Z__flat.shape, label_value, dtype=np.int8)
    for _ in range(6):
        agent.reset_state()
        agent.next_state(INPUT=current, LABEL=label, print_result=False, unsequenced=True)


st.title("Open-Source Issue Recommender")
st.write(
    "Pick the kind of contribution you want to make. The demo maps each task to the same "
    "8-bit AO input shape as the original recommender, then ranks the best next issues for you."
)

with st.sidebar:
    st.header("Contributor context")
    goal = st.selectbox("Goal", ("learn", "quick-win", "portfolio", "maintainer"))
    max_minutes = st.slider("Time available", min_value=20, max_value=180, value=60, step=5)
    preferred_tracks = st.multiselect(
        "Preferred tracks",
        options=list(TRACK_BITS.keys()),
        default=["bug", "tests", "docs"],
    )
    st.caption(
        "AO input: 3 bits track, 2 bits difficulty, 1 bit task size, 2 bits contributor goal."
    )

results = recommend_issues(preferred_tracks, goal, max_minutes, limit=6)

for index, item in enumerate(results):
    issue = item["issue"]
    ao_score = agent_score(item["encoding"])
    if index == 0:
        st.session_state.current_issue_encoding = item["encoding"]

    with st.container(border=True):
        cols = st.columns([0.75, 0.25])
        with cols[0]:
            st.subheader(issue.title)
            st.write(issue.summary)
            st.caption(
                f"{issue.project} | {issue.track} | {issue.difficulty} | "
                f"{issue.minutes} min | impact {issue.impact}/10"
            )
            st.code("".join(str(bit) for bit in item["encoding"]), language="text")
        with cols[1]:
            st.metric("Fallback score", item["score"])
            if ao_score is not None:
                st.metric("AO agent score", f"{ao_score}%")
            else:
                st.info("Install ao_core and ao_arch to enable live AO scoring/training.")

if ao is not None and arch is not None:
    col_like, col_less = st.columns(2)
    with col_like:
        if st.button("Recommend more like the top issue", type="primary"):
            train_current(1)
            st.rerun()
    with col_less:
        if st.button("Recommend fewer like the top issue"):
            train_current(0)
            st.rerun()
