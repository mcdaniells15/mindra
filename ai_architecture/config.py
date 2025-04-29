import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config:
    # API Configuration
    API_KEY = os.getenv("GOOGLE_API_KEY")
    API_MODEL = "gemini-2.0-flash"
    
    # Security Settings
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    ALLOWED_FILE_TYPES = ["pdf", "pptx", "ppt", "doc", "docx"]
    RATE_LIMIT = 100  # requests per minute
    
    # Performance Settings 
    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 200
    MAX_CONCURRENT_REQUESTS = 10
    
    # Difficulty Levels
    DIFFICULTY_LEVELS: Dict[str, Dict[str, Any]] = {
        "beginner": {
            "prompt": "Provide simple, easy-to-understand explanations with basic examples. Focus on fundamental concepts and everyday applications.",
            "max_complexity": 1
        },
        "intermediate": {
            "prompt": "Provide detailed explanations with real-world examples. Include step-by-step processes and practical applications.",
            "max_complexity": 2
        },
        "advanced": {
            "prompt": "Provide in-depth explanations with complex examples. Include advanced applications, edge cases, and industry-specific implementations.",
            "max_complexity": 3
        }
    }
    
    @classmethod
    def get_difficulty_prompt(cls, difficulty: str) -> str:
        return cls.DIFFICULTY_LEVELS.get(difficulty, cls.DIFFICULTY_LEVELS["intermediate"])["prompt"] 