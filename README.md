# AO Labs Recommender System

A recommender system built with AO Labs' post-training learning architecture. The system learns from user behavior in real-time, providing increasingly personalized recommendations.

## Domains

This recommender has been adapted to multiple domains:

- **YouTube** (original) - Video recommendations based on genre and mood
- **Programming Education** - Coding tutorial and course recommendations based on skill level and interests

## Quick Start

### YouTube Recommender
```bash
pip install -r requirements.txt
streamlit run main.py
```

### Programming Education Recommender
```bash
pip install -r requirements.txt
streamlit run coding_edu_recommender.py
```

## Programming Education Domain

The coding education recommender suggests programming tutorials, courses, and practice resources based on:

- **Topic**: Web Dev, Mobile, Data Science, AI/ML, Systems, DevOps, Game Dev, Blockchain, IoT, Security
- **Difficulty**: Beginner, Intermediate, Advanced
- **Format**: Video, Interactive/Hands-on
- **Experience**: No experience, Some basics, Experienced, Senior

The system uses AO Labs' binary encoding architecture with 8-bit input vectors to represent user preferences and learn from feedback.

## Architecture

Each domain has its own architecture file:
- `arch__Recommender.py` - YouTube recommender architecture
- `arch__CodingEduRecommender.py` - Programming education architecture

## Testing

```bash
python -m pytest tests/test_coding_edu.py -v
```

## License

See original repository for license information.
