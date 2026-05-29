# -*- coding: utf-8 -*-
"""
Programming Education Resource Domain Data
Catalog of coding learning resources for the recommender system.
"""

# Topic categories (10 topics, 3-bit binary encoding)
TOPIC_MAP = {
    0: "Web Development",
    1: "Mobile Development", 
    2: "Data Science",
    3: "AI/Machine Learning",
    4: "Systems Programming",
    5: "DevOps/Cloud",
    6: "Game Development",
    7: "Blockchain/Crypto",
    8: "Embedded/IoT",
    9: "Security"
}

# Difficulty levels (2-bit encoding)
DIFFICULTY_MAP = {
    0: "Beginner",
    1: "Intermediate",
    2: "Advanced",
    3: "Expert"
}

# Format types (1-bit encoding)
FORMAT_MAP = {
    0: "Video",
    1: "Interactive/Hands-on"
}

# Experience levels (2-bit encoding)
EXPERIENCE_MAP = {
    0: "No prior experience",
    1: "Some programming (basics)",
    2: "Experienced developer",
    3: "Senior/Expert"
}

# Resource catalog - 12 items covering diverse programming topics
RESOURCE_CATALOG = [
    {
        "id": 0,
        "title": "HTML & CSS Fundamentals",
        "topic": "Web Development",
        "difficulty": "Beginner",
        "format": "Interactive",
        "experience": "No prior experience",
        "description": "Learn the building blocks of the web with hands-on exercises",
        "url": "https://www.freecodecamp.org/learn/responsive-web-design/",
        "duration": "300 hours",
        "tags": ["html", "css", "responsive", "web"]
    },
    {
        "id": 1,
        "title": "React Complete Guide",
        "topic": "Web Development",
        "difficulty": "Intermediate",
        "format": "Video",
        "experience": "Some programming (basics)",
        "description": "Build modern web apps with React hooks, state management, and routing",
        "url": "https://react.dev/learn",
        "duration": "40 hours",
        "tags": ["react", "javascript", "frontend", "hooks"]
    },
    {
        "id": 2,
        "title": "Flutter Mobile App Development",
        "topic": "Mobile Development",
        "difficulty": "Intermediate",
        "format": "Interactive",
        "experience": "Some programming (basics)",
        "description": "Build cross-platform mobile apps with Flutter and Dart",
        "url": "https://flutter.dev/learn",
        "duration": "30 hours",
        "tags": ["flutter", "dart", "mobile", "cross-platform"]
    },
    {
        "id": 3,
        "title": "Python for Data Analysis",
        "topic": "Data Science",
        "difficulty": "Beginner",
        "format": "Interactive",
        "experience": "No prior experience",
        "description": "Learn pandas, numpy, and matplotlib for data analysis",
        "url": "https://www.kaggle.com/learn/pandas",
        "duration": "20 hours",
        "tags": ["python", "pandas", "data-analysis", "visualization"]
    },
    {
        "id": 4,
        "title": "Deep Learning Specialization",
        "topic": "AI/Machine Learning",
        "difficulty": "Advanced",
        "format": "Video",
        "experience": "Experienced developer",
        "description": "Master neural networks, CNNs, RNNs, and transformers",
        "url": "https://www.deeplearning.ai/courses/deep-learning-specialization/",
        "duration": "120 hours",
        "tags": ["deep-learning", "neural-networks", "cnn", "transformers"]
    },
    {
        "id": 5,
        "title": "Rust Systems Programming",
        "topic": "Systems Programming",
        "difficulty": "Advanced",
        "format": "Interactive",
        "experience": "Experienced developer",
        "description": "Learn Rust for safe, concurrent systems programming",
        "url": "https://doc.rust-lang.org/book/",
        "duration": "60 hours",
        "tags": ["rust", "systems", "memory-safety", "concurrency"]
    },
    {
        "id": 6,
        "title": "Docker & Kubernetes in Practice",
        "topic": "DevOps/Cloud",
        "difficulty": "Intermediate",
        "format": "Interactive",
        "experience": "Some programming (basics)",
        "description": "Containerize apps and orchestrate with Kubernetes",
        "url": "https://kubernetes.io/docs/tutorials/",
        "duration": "40 hours",
        "tags": ["docker", "kubernetes", "containers", "devops"]
    },
    {
        "id": 7,
        "title": "Unity Game Development Bootcamp",
        "topic": "Game Development",
        "difficulty": "Beginner",
        "format": "Video",
        "experience": "No prior experience",
        "description": "Build 2D and 3D games with Unity and C#",
        "url": "https://learn.unity.com/",
        "duration": "50 hours",
        "tags": ["unity", "csharp", "gamedev", "3d"]
    },
    {
        "id": 8,
        "title": "Smart Contract Development with Solidity",
        "topic": "Blockchain/Crypto",
        "difficulty": "Intermediate",
        "format": "Interactive",
        "experience": "Some programming (basics)",
        "description": "Build decentralized applications on Ethereum",
        "url": "https://cryptozombies.io/",
        "duration": "20 hours",
        "tags": ["solidity", "ethereum", "smart-contracts", "web3"]
    },
    {
        "id": 9,
        "title": "ESP32 IoT Projects",
        "topic": "Embedded/IoT",
        "difficulty": "Intermediate",
        "format": "Interactive",
        "experience": "Some programming (basics)",
        "description": "Build IoT projects with ESP32, sensors, and MQTT",
        "url": "https://docs.espressif.com/projects/esp-idf/en/latest/esp32/get-started/",
        "duration": "30 hours",
        "tags": ["esp32", "iot", "sensors", "mqtt"]
    },
    {
        "id": 10,
        "title": "OWASP Web Security Fundamentals",
        "topic": "Security",
        "difficulty": "Intermediate",
        "format": "Interactive",
        "experience": "Experienced developer",
        "description": "Learn web application security, OWASP Top 10, and penetration testing basics",
        "url": "https://owasp.org/www-project-web-security-learning/",
        "duration": "25 hours",
        "tags": ["security", "owasp", "pentesting", "web-security"]
    },
    {
        "id": 11,
        "title": "Full-Stack JavaScript Mastery",
        "topic": "Web Development",
        "difficulty": "Advanced",
        "format": "Video",
        "experience": "Senior/Expert",
        "description": "Master Node.js, Express, databases, deployment, and microservices",
        "url": "https://nodejs.org/en/learn",
        "duration": "80 hours",
        "tags": ["nodejs", "express", "fullstack", "microservices"]
    }
]

def get_topic_encoding(topic_name):
    for k, v in TOPIC_MAP.items():
        if v == topic_name:
            return k
    return 0

def get_difficulty_encoding(difficulty_name):
    for k, v in DIFFICULTY_MAP.items():
        if v == difficulty_name:
            return k
    return 0

def get_format_encoding(format_name):
    for k, v in FORMAT_MAP.items():
        if v == format_name:
            return k
    return 0

def get_experience_encoding(experience_name):
    for k, v in EXPERIENCE_MAP.items():
        if v == experience_name:
            return k
    return 0
