# AO Labs Music Recommender

A personalized music recommendation system that learns from your feedback in real-time. Unlike traditional recommender systems that rely on collaborative filtering (comparing your usage to others), this system learns your specific preferences and adapts to your current mood.

## Features

- **Real-time Learning**: The system continuously learns from your feedback, adapting its recommendations to your preferences.
- **Mood-based Recommendations**: Set your current mood (Energetic, Relaxed, Focused) and get appropriate music recommendations.
- **Rich Music Features**: Uses Spotify's audio features including:
  - Genre classification using OpenAI embeddings
  - Tempo analysis (slow/medium/fast)
  - Energy levels
  - Danceability scores
- **Embedded Player**: Preview songs directly in the app using Spotify's embedded player.
- **Training History**: View your interaction history and how the agent learns from your preferences.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/aolabsai/recommender.git
cd recommender
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env_example` to `.env`
- Add your API keys:
  - Get Spotify API credentials from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
  - Get OpenAI API key from [OpenAI](https://platform.openai.com/api-keys)

4. Run the music recommender:
```bash
streamlit run music_recommender.py
```

## How It Works

1. **Feature Extraction**:
   - Genre classification using OpenAI embeddings
   - Audio features from Spotify API:
     - Tempo: Categorized as slow (<90 BPM), medium (90-120 BPM), or fast (>120 BPM)
     - Energy: Spotify's measure of intensity and activity
     - Danceability: How suitable a track is for dancing
   - User's current mood

2. **Binary Encoding**:
   The system converts all features into binary format:
   - Genre: 3 bits (supporting up to 8 genre categories)
   - Tempo: 2 bits (slow/medium/fast)
   - Energy: 2 bits (low/medium/high)
   - Danceability: 2 bits (low/medium/high)
   - Mood: 2 bits (Energetic/Relaxed/Focused/Random)

3. **Recommendation Process**:
   - The AO Agent processes the binary features
   - Learns associations between features and user preferences
   - Adapts recommendations based on mood context
   - Filters out low-confidence recommendations

4. **Continuous Learning**:
   - Like/Dislike feedback trains the agent
   - The system adapts to your preferences in real-time
   - Different moods can have different preferences
   - Training history is maintained for transparency

## Usage

1. Select your current mood from the sidebar:
   - Energetic: For upbeat, high-energy music
   - Relaxed: For calm, soothing tracks
   - Focused: For concentration and work
   - Random: For general exploration

2. Click "Get Next Track" to start getting recommendations

3. For each track:
   - 👍 Like: Trains the agent to recommend similar tracks
   - 👎 Dislike: Trains the agent to avoid similar tracks
   - ⏭️ Skip: Moves to next track without training

4. View your training history in the sidebar to understand how the agent learns from your preferences

## Contributing

We welcome contributions! Some areas for improvement:
- Additional audio features from Spotify API
- More sophisticated genre classification
- Enhanced mood detection
- UI/UX improvements
- Performance optimizations

Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [AO Labs](https://www.aolabs.ai/) technology
- Uses [Spotify Web API](https://developer.spotify.com/documentation/web-api)
- Powered by [OpenAI](https://openai.com/) for embeddings