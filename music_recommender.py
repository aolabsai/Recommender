import streamlit as st
import os
import random
import numpy as np
import pandas as pd
import requests
import time
import streamlit_analytics2
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

# AO Labs imports (these are your custom modules, presumably unchanged)
import ao_core as ao
from arch__MusicRecommender import arch
import embedding_bucketing.embedding_model_test as em

# Spotify handling
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

#############################
# Setup Spotify Credentials #
#############################
SPOTIPY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')

if not SPOTIPY_CLIENT_ID or not SPOTIPY_CLIENT_SECRET:
    st.error("Spotify credentials not set. Please set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.")
    st.stop()

auth_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

################################
# Session State Initialization #
################################
if "tracks_in_list" not in st.session_state:
    st.session_state.tracks_in_list = []
if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = []
if "current_binary_input" not in st.session_state:
    st.session_state.current_binary_input = []
if "training_history" not in st.session_state:
    st.session_state.training_history = (np.zeros([1000,7], dtype="O"))
    st.session_state.numberVideos = 0
if "mood" not in st.session_state:
    st.session_state.mood = "Random"
if "display_track" not in st.session_state:
    st.session_state.display_track = False
if "natural_language_input" not in st.session_state:
    st.session_state.natural_language_input = None
if "recommended" not in st.session_state:
    st.session_state.recommended = False
if "number_tracks_not_recommended" not in st.session_state:
    st.session_state.number_tracks_not_recommended = 0
    st.session_state.threshold = 50

if "agent" not in st.session_state:
    print("-------creating agent-------")
    st.session_state.agent = ao.Agent(arch, notes="Default Agent")
    for i in range(4):
        st.session_state.agent.reset_state()
        st.session_state.agent.reset_state(training=True)


###################################
# Embedding bucketing configuration
###################################
max_distance = 20
amount_of_binary_digits = 3
type_of_distance_calc = "COSINE SIMILARITY"
start_Genre = ["Pop", "Rock", "Hip Hop", "Jazz", "Classical", "Electronic", "R&B", "Country", "Metal", "Folk"]
em.config(openai_api_key)
print("configuring em")

if "cache" not in st.session_state:
    cache_file_name = "music_genre_embedding_cache.json"
    st.session_state.cache, st.session_state.genre_buckets = em.init(cache_file_name, start_Genre)
    print("init em")

###########################
# Functions for Recommender
###########################

def embedding_bucketing_response(cache, uncategorized_input, max_distance, bucket_list, type_of_distance_calc, amount_of_binary_digits):
    sort_response = em.auto_sort(cache, uncategorized_input, max_distance, bucket_list, type_of_distance_calc, amount_of_binary_digits)  
    closest_distance = sort_response[0]
    closest_bucket   = sort_response[1]  
    bucket_id        = sort_response[2]
    bucket_binary    = sort_response[3]
    return closest_bucket, bucket_binary

def get_mood_binary():
    mood = st.session_state.mood.upper()
    if mood == "RANDOM":
        mood_binary = [1,1]
    elif mood == "RELAXED":
        mood_binary = [0,1]
    elif mood == "FOCUSED":
        mood_binary = [1,0]
    elif mood == "PARTY":
        mood_binary = [0,0]
    else:  # CHILL as default
        mood_binary = [1,1]
    return mood_binary, st.session_state.mood

def sort_agent_response(agent_response):
    count = sum([1 for e in agent_response if e == 1])
    percentage = (count / len(agent_response)) * 100 
    return percentage

def prepare_for_next_track(user_feedback):  #Only run once per track
    print("running pfnv")
    if st.session_state.natural_language_input:
        st.session_state.training_history[st.session_state.numberVideos, :] = st.session_state.natural_language_input
        print("Added", st.session_state.natural_language_input, "to agent history")

    st.session_state.numberVideos += 1

    if len(st.session_state.tracks_in_list) > 1:
        st.session_state.tracks_in_list.pop(0)
        st.session_state.display_track = True
        st.session_state.training_history[st.session_state.numberVideos - 1, -1] = user_feedback

def agent_response(binary_input):
    st.session_state.agent.reset_state()
    last_response = 0
    for i in range(5):
        response = st.session_state.agent.next_state(INPUT=binary_input, print_result=False)
        if i == 4:
            last_response = response
    return last_response

def train_agent(user_response):
    st.session_state.agent.reset_state()
    binary_input = st.session_state.current_binary_input
    if user_response == "RECOMMEND MORE":
        Cpos = True 
        Cneg = False
        label  = np.ones(st.session_state.agent.arch.Z__flat.shape, dtype=np.int8)
        size = 5
    elif user_response == "STOP RECOMMENDING":
        Cneg = True
        Cpos = False
        label = np.zeros(st.session_state.agent.arch.Z__flat.shape, dtype=np.int8)
        size = 10

    for i in range(size):
        st.session_state.agent.reset_state()
        st.session_state.agent.next_state(INPUT=binary_input, LABEL=label, print_result=False, unsequenced=True)


##########################
# Spotify-related Methods #
##########################

def search_spotify_track_for_genre(genre):
    # We'll do a search for genre + "music", limit results, and pick randomly
    # Using the 'track' type search
    query = genre + " music"
    results = sp.search(q=query, type='track', limit=20)
    tracks = results.get('tracks', {}).get('items', [])
    if tracks:
        # Return a random track from these results
        return random.choice(tracks)
    return None

def get_random_spotify_track():
    # Picks a random genre from start_Genre and searches tracks
    genre = random.choice(start_Genre)
    track_info = search_spotify_track_for_genre(genre)
    return track_info

def get_spotify_track_data(track):
    # Extract info: title, preview_url, track length in ms, etc.
    title = track['name']
    
    # Fix: Use 'artists' instead of 'artist'
    artists = ", ".join([artist['name'] for artist in track['artists']])
    
    track_length_ms = track['duration_ms']
    length_minutes = round((track_length_ms / 60000), 2)
    preview_url = track['preview_url']

    # Embedding bucketing and classification
    closest_genre, genre_binary_encoding = embedding_bucketing_response(
        st.session_state.cache, title, max_distance, st.session_state.genre_buckets, type_of_distance_calc, amount_of_binary_digits
    )
    genre_binary_encoding = genre_binary_encoding.tolist()[:3]  # Limit to 3 bits

    # length_binary: short <5 min = [0,0], medium 5-20 min = [0,1], long >20 min [1,1]
    if length_minutes < 5:
        length_binary = [0,0]
    elif 5 <= length_minutes < 20:
        length_binary = [0,1]
    else:
        length_binary = [1,1]

    return title, preview_url, length_minutes, length_binary, closest_genre, genre_binary_encoding, artists

def next_track():
    data = get_random_spotify_track()
    while not data:
        data = get_random_spotify_track()

    track_id = data['id']
    if track_id not in st.session_state.tracks_in_list:
        st.session_state.tracks_in_list.append(track_id)
    st.session_state.display_track = True

    title, preview_url, length, length_binary, closest_genre, genre_binary_encoding, artists = get_spotify_track_data(data)
    mood_binary, mood = get_mood_binary()

    # Combine binaries for agent input (7 bits total)
    binary_input_to_agent = genre_binary_encoding + length_binary + mood_binary
    
    # Debug print to check lengths
    print(f"Genre bits: {len(genre_binary_encoding)}, Length bits: {len(length_binary)}, Mood bits: {len(mood_binary)}")
    print(f"Total bits: {len(binary_input_to_agent)}")
    
    # Force to exactly 7 bits if needed
    if len(binary_input_to_agent) != 7:
        print(f"Warning: Input length mismatch. Expected 7, got {len(binary_input_to_agent)}")
        binary_input_to_agent = binary_input_to_agent[:7]
    
    st.session_state.current_binary_input = binary_input_to_agent
    st.session_state.recommendation_result = agent_response(binary_input_to_agent)
    percentage_response = sort_agent_response(st.session_state.recommendation_result) 
    recommended = (str(percentage_response) +"%")

    st.session_state.natural_language_input = [title, closest_genre, length, artists, mood, recommended, "User's Training"]

    if percentage_response >= st.session_state.threshold:
        if st.session_state.threshold < 50:
            st.session_state.threshold += 10
        
        st.markdown(f"**Genre:** {closest_genre}")
        st.markdown(f"**Artist:** {artists}")  # Moved here, right after genre
        st.markdown(f"**User's Mood:** {mood}")
        st.write("**Agent's Recommendation:**", recommended)
        
        if st.session_state.number_tracks_not_recommended > 0:
            skip_text = f"{st.session_state.number_tracks_not_recommended} tracks were skipped"
            st.markdown(skip_text)
        
        st.session_state.number_tracks_not_recommended = 0
        
        # Embed Spotify player
        st.components.v1.iframe(
            f"https://open.spotify.com/embed/track/{track_id}",
            height=80
        )
    else:
        if st.session_state.number_tracks_not_recommended > 5:
            st.session_state.threshold -= 10
            print("Brought threshold down to ", st.session_state.threshold)
        st.session_state.number_tracks_not_recommended += 1
        prepare_for_next_track(user_feedback="Track not recommended")
        genre, genre_binary_encoding = next_track()

    return closest_genre, genre_binary_encoding


#####################
# STREAMLIT UI START
#####################
streamlit_analytics2.start_tracking()

st.set_page_config(
    page_title="Personal Music Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://discord.gg/Zg9bHPYss5",
        "Report a bug": "mailto:eng@aolabs.ai",
        "About": "AO Labs builds next-gen AI models that learn after training; learn more at docs.aolabs.ai/docs/mnist-benchmark",
    },
)

with st.sidebar:
    st.write("## Current Active Agent:")
    st.write(st.session_state.agent.notes)

    # Loading and saving agents
    import os

    st.write("---")
    st.write("## Load Agent:")

    def load_pickle_files(directory):
        pickle_files = [
            f[:-10] for f in os.listdir(directory) if f.endswith(".ao.pickle")
        ]
        return pickle_files

    directory = os.path.dirname(os.path.abspath(__file__))
    pickle_files = load_pickle_files(directory)
    if pickle_files:
        selected_file = st.selectbox("Choose from saved Agents:", options=pickle_files)
        if st.button(f"Load {selected_file}"):
            file_path = os.path.join(directory, selected_file)
            st.session_state.agent = ao.Agent.unpickle(file=file_path, custom_name=selected_file)
            st.session_state.agent._update_neuron_data()
            st.write("Agent loaded")
    else:
        st.warning("No Agents saved yet-- be the first!")

    st.write("---")
    st.write("## Save Agent:")
    agent_name = st.text_input("## *Optional* Rename active Agent:", value=st.session_state.agent.notes)
    st.session_state.agent.notes = agent_name

    @st.dialog("Save successful!")
    def save_modal_dialog():
        st.write("Agent saved to your local disk.")

    agent_name = agent_name.split("\\")[-1].split(".")[0]
    if st.button("Save " + agent_name):
        st.session_state.agent.pickle(agent_name)
        save_modal_dialog()

    st.write("---")
    st.write("## Download/Upload Agents:")

    @st.dialog("Upload successful!")
    def upload_modal_dialog():
        st.write("Agent uploaded and ready as *Newly Uploaded Agent*.")

    uploaded_file = st.file_uploader("Upload .ao.pickle files here", label_visibility="collapsed")
    if uploaded_file is not None:
        if st.button("Confirm Agent Upload"):
            st.session_state.agent = ao.Agent.unpickle(uploaded_file, custom_name="Newly Uploaded Agent", upload=True)
            st.session_state.agent._update_neuron_data()
            upload_modal_dialog()

    @st.dialog("Download ready")
    def download_modal_dialog(agent_pickle):
        st.write("The Agent's .ao.pickle file is ready for download.")
        st.download_button(
            label="Download Agent: " + st.session_state.agent.notes,
            data=agent_pickle,
            file_name=st.session_state.agent.notes,
            mime="application/octet-stream",
        )

    if st.button("Prepare Active Agent for Download"):
        agent_pickle = st.session_state.agent.pickle(download=True)
        download_modal_dialog(agent_pickle)


st.title("Personal Music Recommender (Spotify Edition)")
st.write("### *a preview by [aolabs.ai](https://www.aolabs.ai/)*")

with st.expander("How this app works:", expanded=True):
    explain_txt = '''
    This recommender demonstrates per-user adaptive training using your feedback and AO's Weightless Neural Network Agent.
    
    - We fetch random tracks from Spotify (by genre).
    - The AO Agent provides a recommendation score.
    - You set a mood and provide feedback:
      - "Recommend More" to reinforce the Agent's preferences.
      - "Stop Recommending" to discourage certain tracks.
    - Over time, the Agent learns what music to present based on your mood and feedback.
    '''
    st.markdown(explain_txt)

st.session_state.mood = st.selectbox("Set your music mood:", ("Random", "Relaxed", "Focused", "Party", "Chill"))
st.write("Track number: ", str(st.session_state.numberVideos))

small_right, small_left = st.columns(2)
if small_right.button(":green[RECOMMEND MORE]", type="primary"):
    train_agent(user_response="RECOMMEND MORE")
    user_feedback = "More"
    prepare_for_next_track(user_feedback)

if small_left.button(":red[STOP RECOMMENDING]"):
    train_agent(user_response="STOP RECOMMENDING")
    user_feedback = "Less"
    prepare_for_next_track(user_feedback)

genre, genre_binary_encoding = next_track()

if st.session_state.display_track == True:
    with st.expander("### Agent's Training History"):
        history_titles = ["Title", "Closest Genre", "Duration", "Type", "User's Mood", "Agent's Recommendation", "User's Training" ]
        df = pd.DataFrame(st.session_state.training_history[0:st.session_state.numberVideos, :], columns=history_titles)
        st.dataframe(df)

st.write("---")
footer_md = """
[View & fork the code behind this application here.](https://github.com/aolabsai/Recommender) \n
To learn more about AO Labs and Weightless Neural Networks, [visit docs.aolabs.ai.](https://docs.aolabs.ai/)  
[Join our discord to say hi!](https://discord.gg/Zg9bHPYss5)
"""
st.markdown(footer_md)

st.image("misc/aolabs-logo-horizontal-full-color-white-text.png", width=300)

streamlit_analytics2.stop_tracking()