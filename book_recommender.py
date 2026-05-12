import streamlit as st

from book_domain import BOOK_CATALOG, encode_book, recommend_books

try:
    import ao_core as ao
    from arch__BookRecommender import arch
except Exception:
    ao = None
    arch = None


def get_agent():
    if ao is None or arch is None:
        return None
    if "book_agent" not in st.session_state:
        st.session_state.book_agent = ao.Agent(arch, notes="Book Recommender Agent")
        for _ in range(4):
            st.session_state.book_agent.reset_state()
            st.session_state.book_agent.reset_state(training=True)
    return st.session_state.book_agent


def agent_vote(agent, book, mood):
    if agent is None:
        return None
    agent.reset_state()
    response = agent.next_state(encode_book(book, mood))
    if not response:
        return 0
    return round(sum(response) / len(response) * 100, 1)


st.set_page_config(page_title="AO Book Recommender")
st.title("AO Book Recommender")

st.caption(
    "A local book-domain demo for applying the AO recommender pattern without paid APIs."
)

genre = st.selectbox(
    "Preferred genre",
    ["science_fiction", "fantasy", "self_improvement", "memoir", "nature", "productivity", "design"],
)
pace = st.selectbox("Reading pace", ["gentle", "medium", "fast", "slow"])
length = st.selectbox("Book length", ["short", "medium", "long"])
tone = st.selectbox("Tone", ["cozy", "hopeful", "practical", "reflective", "witty", "epic"])
book_format = st.selectbox("Format", ["novel", "novella", "nonfiction"])
mood = st.selectbox(
    "Current reading context",
    ["comfort", "curious", "focused", "fun", "adventurous", "thoughtful", "motivated", "relaxed", "calm", "immersive"],
)

preferences = {
    "genre": genre,
    "pace": pace,
    "length": length,
    "tone": tone,
    "format": book_format,
    "mood": mood,
}

agent = get_agent()
if agent is None:
    st.info("AO packages are not installed; using deterministic local fallback scoring.")

for book in recommend_books(preferences, BOOK_CATALOG, limit=3):
    vote = agent_vote(agent, book, mood)
    with st.container(border=True):
        st.subheader(book["title"])
        st.write(
            f"{book['genre']} · {book['pace']} pace · {book['length']} · "
            f"{book['tone']} · {book['format']}"
        )
        st.write("Reader contexts: " + ", ".join(book["context"]))
        if vote is not None:
            st.write(f"AO recommendation signal: {vote}%")
