import streamlit as st
import os
# for getting random links
import scrapetube 
import random
#to convert numpy array to list
import numpy as np
import pandas as pd
## for getting title
import requests
import streamlit_analytics2

#for getting youtube length
from pytube import YouTube
#for bucketing
import embedding_bucketing.embedding_model_test as em
#own modules ao_core arch
import ao_core as ao
from arch__Recommender import arch

# openai api key for embedding model
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

import time
# Initialize global variables
if "videos_in_list" not in st.session_state:
    st.session_state.videos_in_list = []
if "recommendation_result" not in st.session_state:
    st.session_state.recommendation_result = []
if "current_binary_input" not in st.session_state:
    st.session_state.current_binary_input = []
if "training_history" not in st.session_state:
    st.session_state.training_history = (np.zeros([1000,7], dtype="O"))
    st.session_state.numberVideos = 0
if "mood" not in st.session_state:
    st.session_state.mood = "Random"
if "display_video" not in st.session_state:
    st.session_state.display_video = False
if "natural_language_input" not in st.session_state:
    st.session_state.natural_language_input = None
if "recommened" not in st.session_state:
    st.session_state.recommended = False
if "number_videos_not_recommended" not in st.session_state:
    st.session_state.number_videos_not_recommended = 0
    st.session_state.threshold = 50
#init agent
if "agent" not in st.session_state:
    print("-------creating agent-------")
    st.session_state.agent = ao.Agent(arch, notes="Default Agent")
    
# intially train on random inputs 
    for i in range(4):
        st.session_state.agent.reset_state()
        st.session_state.agent.reset_state(training=True)


# Constants for embedding bucketing
max_distance = 20 # setting it high for no auto bucketing
amount_of_binary_digits = 3
type_of_distance_calc = "COSINE SIMILARITY"
# start_Genre = ["Drama", "Comedy", "Action", "Romance", "Documentary", "Music", "Gaming", "Entertainment", "News", "Thriller", "Horror", "Science Fiction", "Fantasy", "Adventure", "Mystery", "Animation", "Historical"]
start_Genre = ["Comedy", "News", "Music", "Podcast", "Documentary"]

em.config(openai_api_key) # configuring openai client for embedding model
print("configuring em")

if "cache" not in st.session_state:
    cache_file_name = "genre_embedding_cache.json"
    st.session_state.cache, st.session_state.genre_buckets = em.init(cache_file_name, start_Genre)
    print("init em")


# Predefined list of random search terms
# random_search_terms = ['funny', 'gaming', 'science', 'technology', 'news', 'random', 'adventure', "programming", "history", "podcast", "romance", "animation", "current events"]
random_search_terms = start_Genre

def get_random_youtube_link():  
    # Select a random search term
    search_term = random.choice(random_search_terms)
    
    # Get videos from scrapetube
    videos = scrapetube.get_search(query=search_term, limit=10)
    
    # Shuffle and pick a random video
    video_list = list(videos)
    random.shuffle(video_list)
    
    if video_list:
        random_video = random.choice(video_list)
        video_id = random_video.get('videoId')
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
    
    return None

def get_title_from_url(url):
    # YouTube oEmbed API endpoint
    oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
    
    # Send a request to the oEmbed API
    response = requests.get(oembed_url)
    
    if response.status_code == 200:
        # Extract the title from the JSON response
        data = response.json()
        return data['title']
    else:
        st.write("Error: Unable to fetch title")
        return "Error: Unable to fetch video title."

def get_FNF_from_title(title):
    input_message = ("Is this following video title fiction or not? Title: "+ title)
    response = em.llm_call(input_message)
    response = response.upper() # Making the response upper case for no ambiguity
    fnf_binary = []
    if "FICTION" in response:
        fnf_binary = [1]
        response = "Fiction"
    else:
        fnf_binary = [0]
        response = "Non-fiction"
    return fnf_binary, response

def get_length_from_url(url): # returns if the video is short, medium or long in binary
    yt = YouTube(url)
    try:
        length = yt.length
    except Exception as e:
        print("error in getting length", e)
        length = 0
    length = round(length / 60, 2)
    length_binary = []
    if length < 5:
        length_binary = [0, 0]
    elif length >= 5 and length < 20:
        length_binary = [0, 1]
    else:
        length_binary = [1, 1]
    return length, length_binary

def get_video_data_from_url(url):
    length, length_binary = get_length_from_url(url)
    title = get_title_from_url(url)
    closest_genre, genre_binary_encoding = embedding_bucketing_response(st.session_state.cache, title, max_distance, st.session_state.genre_buckets, type_of_distance_calc, amount_of_binary_digits)
    genre_binary_encoding = genre_binary_encoding.tolist()
    fnf_binary, fnf = get_FNF_from_title(title)
    return length, length_binary, closest_genre, genre_binary_encoding, fnf, fnf_binary

def embedding_bucketing_response(cache, uncategorized_input, max_distance, bucket_list, type_of_distance_calc, amount_of_binary_digits):
    sort_response = em.auto_sort(cache, uncategorized_input, max_distance, bucket_list, type_of_distance_calc, amount_of_binary_digits)  

    closest_distance = sort_response[0]
    closest_bucket   = sort_response[1]  # which bucket the uncategorized_input was placed in
    bucket_id        = sort_response[2]  # the id of the closest_bucket
    bucket_binary    = sort_response[3]  # binary representation of the id for INPUT into api.aolabs.ai

    return closest_bucket, bucket_binary # returning the closest bucket and its binary encoding

def Get_mood_binary():
    mood = st.session_state.mood.upper()
    # converting mood to binary here
    if mood == "RANDOM":
        mood_binary = [1,0]
    elif mood == "SERIOUS":
        mood_binary = [1,1]
    elif mood == "FUNNY":
        mood_binary = [0,1]
    else:
        mood_binary = [0,0] # if mood is not defined then give it 0,0
    return mood_binary, st.session_state.mood

def sort_agent_response(agent_response):
    #st.write("Agent response in binary: ", agent_response)
    count = 0
    for element in agent_response:
        if element == 1:  
            count += 1
    percentage = (count / len(agent_response)) * 100 
    return percentage


def prepare_for_next_video(user_feedback):  #Only run once per video
    print("running pfnv")

    # Update the training history for the current video, based on user feedback
    if st.session_state.natural_language_input:
        st.session_state.training_history[st.session_state.numberVideos, :] = st.session_state.natural_language_input
        print("Added", st.session_state.natural_language_input, "to agent history")

    st.session_state.numberVideos += 1

    if len(st.session_state.videos_in_list) > 1:
        st.session_state.videos_in_list.pop(0)  # Remove the first video from the list
        st.session_state.display_video = True
        # Instead of always setting it to "User Disliked," track the actual response
        st.session_state.training_history[st.session_state.numberVideos - 1, -1] = user_feedback  # Store feedback in history



def next_video():  # function return closest genre and binary encoding of next video and displays it 
    data = get_random_youtube_link()
    while not data:  # Retry until a valid link is retrieved
        data = get_random_youtube_link()
    if data not in st.session_state.videos_in_list:
        st.session_state.videos_in_list.append(data)
    st.session_state.display_video = True

    length, length_binary, closest_genre, genre_binary_encoding, fnf, fnf_binary = get_video_data_from_url(st.session_state.videos_in_list[0])
    mood_binary, mood = Get_mood_binary()

    

    # binary_input_to_agent = genre_binary_encoding+ length_binary + fnf_binary +mood_binary
    binary_input_to_agent = genre_binary_encoding + [0,0] + [0] + mood_binary
   # st.write("binary input:", binary_input_to_agent)++
    st.session_state.current_binary_input = binary_input_to_agent # storing the current binary input to reduce redundant calls
    st.session_state.recommendation_result = agent_response(binary_input_to_agent)
    percentage_response = sort_agent_response(st.session_state.recommendation_result) 
    recommended = (str(percentage_response) +"%")



    title = get_title_from_url(st.session_state.videos_in_list[0])
    st.session_state.natural_language_input = [title, closest_genre, length, fnf, mood, recommended, "User's Training"]
    if percentage_response >= st.session_state.threshold:
        if st.session_state.threshold<50:
            st.session_state.threshold += 10  # bring the threshold up once videos are being recommended
        st.markdown("     Genre: "+str(closest_genre), help="Extracted by an LLM")
        # st.markdown("     Length: "+str(length), help="in minutes; extracted via pytube")
        # st.markdown("     Fiction/Non-fiction: "+str(fnf), help="Extracted by an LLM")
        st.markdown("     User's Mood: "+str(mood),  help="Inputted by user")
        st.markdown("")
        st.write("**Agent's Recommendation:**  ", recommended)
        if st.session_state.number_videos_not_recommended > 0: 
            t0 = (str(st.session_state.number_videos_not_recommended) + " videos were skipped to get to the recommendation below")
            t0_help = "The recommender skips videos that are below 50 percent recommendation, in effect learning on the fly to filter for you. If it's being too selective and skipping too many videos, try clicking the **Stop Recommending** to change things up. (If it gets stuck skipping videos, we temporarily reduce the 50 percent threshold.)"
            st.markdown(t0, help=t0_help)
        st.session_state.number_videos_not_recommended = 0
        st.video(st.session_state.videos_in_list[0])
    else:
        if st.session_state.number_videos_not_recommended >5:
            st.session_state.threshold -= 10  #If the recommended is going in a non recommending spiral then we counter that by bring the recommend threshold down
            print("Bought threshold down to ", st.session_state.threshold)
        st.session_state.number_videos_not_recommended += 1
        #if st.button("Next"):
        prepare_for_next_video(user_feedback="Video not recommended")
        genre, genre_binary_encoding = next_video()
    return closest_genre, genre_binary_encoding

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
    
    # st.session_state.agent.next_state(INPUT=binary_input, Cpos=Cpos, Cneg=Cneg, print_result=False)
    for i in range(size):
        st.session_state.agent.reset_state()
        st.session_state.agent.next_state(INPUT=binary_input, LABEL=label, print_result=False, unsequenced=True)


def agent_response(binary_input): # function to get agent response on next video
    #input = get_agent_input()
    st.session_state.agent.reset_state()
    last_response = 0
    for i in range(5):
        response = st.session_state.agent.next_state( INPUT=binary_input, print_result=False)
        print("response:", response)
        if i==4:
            last_response=response
            print("Last response: ", last_response)
    return last_response

streamlit_analytics2.start_tracking()
st.set_page_config(
    page_title="Recommender Demo by AO Labs",
    page_icon="misc/ao_favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://discord.gg/Zg9bHPYss5",
        "Report a bug": "mailto:eng@aolabs.ai",
        "About": "AO Labs builds next-gen AI models that learn after training; learn more at docs.aolabs.ai/docs/mnist-benchmark",
    },
)

############################################################################
with st.sidebar:

    import os

    # def reset_interrupt():
    #     st.session_state.interrupt = False

    # def set_interrupt():
    #     st.session_state.interrupt = True

    st.write("## Current Active Agent:")
    st.write(st.session_state.agent.notes)

    # start_button = st.button(
    #     "Re-Enable Training & Testing",
    #     on_click=reset_interrupt,
    #     help="If you stopped a process\n click to re-enable Testing/Training agents.",
    # )
    # stop_button = st.button(
    #     "Stop Testing",
    #     on_click=set_interrupt,
    #     help="Click to stop a current Test if it is taking too long.",
    # )

    st.write("---")
    st.write("## Load Agent:")

    def load_pickle_files(directory):
        pickle_files = [
            f[:-10] for f in os.listdir(directory) if f.endswith(".ao.pickle")
        ]  # [:-10] is to remove the "ao.pickle" file extension
        return pickle_files

    # directory_option = st.radio(
    #     "Choose directory to retrieve Agents:",
    #     ("App working directory", "Custom directory"),
    #     label_visibility="collapsed"
    # )
    # if directory_option == "App working directory":
    directory = os.path.dirname(os.path.abspath(__file__))
    # else:
    #     directory = st.text_input("Enter a custom directory path:")

    if directory:
        pickle_files = load_pickle_files(directory)

        if pickle_files:
            selected_file = st.selectbox(
                "Choose from saved Agents:", options=pickle_files
            )

            if st.button(f"Load {selected_file}"):
                file_path = os.path.join(directory, selected_file)
                st.session_state.agent = ao.Agent.unpickle(
                    file=file_path, custom_name=selected_file
                )
                st.session_state.agent._update_neuron_data()
                st.write("Agent loaded")
        else:
            st.warning("No Agents saved yet-- be the first!")

    st.write("---")
    st.write("## Save Agent:")

    agent_name = st.text_input(
        "## *Optional* Rename active Agent:", value=st.session_state.agent.notes
    )
    st.session_state.agent.notes = agent_name

    @st.dialog("Save successful!")
    def save_modal_dialog():
        st.write("Agent saved to your local disk (in the same directory as this app).")

    agent_name = agent_name.split("\\")[-1].split(".")[0]
    if st.button("Save " + agent_name):
        st.session_state.agent.pickle(agent_name)
        save_modal_dialog()

    st.write("---")
    st.write("## Download/Upload Agents:")

    @st.dialog("Upload successful!")
    def upload_modal_dialog():
        st.write(
            "Agent uploaded and ready as *Newly Uploaded Agent*, which you can rename during saving."
        )

    uploaded_file = st.file_uploader(
        "Upload .ao.pickle files here", label_visibility="collapsed"
    )
    if uploaded_file is not None:
        if st.button("Confirm Agent Upload"):
            st.session_state.agent = ao.Agent.unpickle(
                uploaded_file, custom_name="Newly Uploaded Agent", upload=True
            )
            st.session_state.agent._update_neuron_data()
            upload_modal_dialog()

    @st.dialog("Download ready")
    def download_modal_dialog(agent_pickle):
        st.write(
            "The Agent's .ao.pickle file will be saved to your default Downloads folder."
        )

        # Create a download button
        st.download_button(
            label="Download Agent: " + st.session_state.agent.notes,
            data=agent_pickle,
            file_name=st.session_state.agent.notes,
            mime="application/octet-stream",
        )

    if st.button("Prepare Active Agent for Download"):
        agent_pickle = st.session_state.agent.pickle(download=True)
        download_modal_dialog(agent_pickle)
############################################################################

# Title of the app
st.title("LLM + WNNs - a Real-Time Personal YouTube Recommender")
st.write("### *a preview by [aolabs.ai](https://www.aolabs.ai/)*")

# big_left, big_right = st.columns([0.3, 0.7], gap="large")

# with big_left:

    # url = st.text_input("Enter link to a YouTube video: ", value=None, placeholder="Optional", help="This app automatically loads YouTube videos, and you can also add a specific YouTube link here.")
    # if url !=None:
    #     if st.button("Add Link"):
    #         try:
    #             if url not in st.session_state.videos_in_list:
    #                 st.session_state.videos_in_list.insert(0, url)
    #                 print(st.session_state.videos_in_list)
    #             else:
    #                 st.write("Unable to add link as it has already been used; please try another")
    #         except Exception as e:
    #             st.write("Error: URL not recognised; please try another")
    #         st.session_state.display_video = True

data = get_random_youtube_link()
while not data:  # Retry until a valid link is retrieved
    data = get_random_youtube_link()

with st.expander("How this app works:", expanded=True, icon=":material/question_mark:"):
    explain_txt = '''
    YouTube recommendations are often impersonal and hard to control-- the ominous *"Algorithm."*

    This app is a preview of a new concept-- a personal recommender that's continuously (re)trained only on your data as you use it; the idea of a recommender as a remote control instead of a pre-trained model trying to get your views.\n
    
    ***How it works:*** an embedding model classifies the video (from its title) as  a specific genre and you as the user can set your mood. There's an AO Agent (see its [architecture here](https://github.com/aolabsai/Recommender/blob/main/arch__Recommender.py)) that learns to associate the genre and mood with your "Recommend More" or "Stop Recommending" button clicks to learn to filter new videos according to your accumulated preferences.  
    
    Below the buttons, you can see the genre, the mood you set, and the percentage of recommendation of the Agent for that particular video. You can then train your Agent by clicking the recommend more or stop buttons.  

    ***Things to try:***
    * see if your AO Agent can learn to recommend a specific genre for you, like News or Podcasts, when you're in a Serious mood.  
    * try unlearning an Agent's recommendations by clicking "Stop Recommending."  
    * if you like an Agent's recommendations, you can save (or even download) it for future sessions using the sidebar to the left.  

    ***Note:*** To make testing easier while in preview mode, the app is fixed on a few genres: Comedy, Music, Documentary, News, Podcast  
    
    Our lightweight systems can easily be extended with more inputs (content-specific inputs like fiction/non-fiction or duration and user-specific inputs like viewing device or day of week) to learn to serve more complicated, nuanced recommendations (eg. maybe you like the News only when you're in a Serious mood on your iPad, and Comedy when in a Random mood on your TV). If you're building a recommender, get in touch to explore the possibilities continuous, per-user training can unlock for your build! [Take a look at the code here.](https://github.com/aolabsai/recommender)
    '''
    st.markdown(explain_txt)
st.session_state.mood = st.selectbox("Set your mood (as the user):", ("Random", "Funny", "Serious"))
st.write("Video number: ", str(st.session_state.numberVideos))
small_right, small_left = st.columns(2)
if small_right.button(":green[RECOMMEND MORE]", type="primary", icon=":material/thumb_up:"):#
    train_agent(user_response="RECOMMEND MORE") # Train agent positively as user like recommendation
    user_feedback = "More"
    prepare_for_next_video(user_feedback)

if small_left.button(":red[STOP RECOMMENDING]", icon=":material/thumb_down:"):
    train_agent(user_response="STOP RECOMMENDING") # train agent negatively as user dislike recommendation
    user_feedback = "Less"
    prepare_for_next_video(user_feedback)

genre, genre_binary_encoding = next_video()
# if st.session_state.display_video == True:


if data not in st.session_state.videos_in_list:
    st.session_state.videos_in_list.append(data)

    with st.expander("### Agent's Training History"):
        history_titles = ["Title", "Closest Genre", "Duration", "Type", "User's Mood", "Agent's Recommendation", "User's Training" ]
        df = pd.DataFrame(
            st.session_state.training_history[0:st.session_state.numberVideos, :], columns=history_titles
            )
        st.dataframe(df)

st.write("---")
footer_md = """
[View & fork the code behind this application here.](https://github.com/aolabsai/Recommender) \n
To learn more about Weightless Neural Networks and the new generation of AI we're developing at AO Labs, [visit our docs.aolabs.ai.](https://docs.aolabs.ai/)\n
\n
We eagerly welcome contributors and hackers at all levels! [Say hi on our discord.](https://discord.gg/Zg9bHPYss5)
"""
st.markdown(footer_md)
st.image("misc/aolabs-logo-horizontal-full-color-white-text.png", width=300)

streamlit_analytics2.stop_tracking()