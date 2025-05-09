import os
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

class Config: 
    # API Configuration
    API_KEY = os.getenv("GOOGLE_API_KEY")
    API_MODEL = "gemini-2.0-flash"
    
    # Batch Processing Settings
    BATCH_PROCESSING = {
        "default_batch_size": int(os.getenv("DEFAULT_BATCH_SIZE", "5")),
        "max_batch_size": int(os.getenv("MAX_BATCH_SIZE", "10")),
        "min_batch_size": int(os.getenv("MIN_BATCH_SIZE", "1")),
        "batch_delay": float(os.getenv("BATCH_DELAY", "0.5")),  # Delay between batches in seconds
        "chunk_size": int(os.getenv("CHUNK_SIZE", "30000")),
        "chunk_overlap": int(os.getenv("CHUNK_OVERLAP", "1000"))
    }
    
    # Security Settings
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
    ALLOWED_FILE_TYPES = ["pdf", "pptx", "ppt", "doc", "docx"]
    
    # Gemini API Limits (Paid Tier 1)
    GEMINI_LIMITS = {
        "requests_per_minute": 2000,     # Gemini's hard limit
        "tokens_per_minute": 4000000,    # Gemini's token limit
        "max_tokens_per_request": 30000  # Maximum tokens per request
    }
    
    # Rate Limit Settings
    RATE_LIMIT_SETTINGS = {
        "global": {
            "limit": 1900,              # Keep slightly under Gemini's 2000 RPM limit for safety
            "window": 60,
            "namespace": "global"
        },
        "user": {
            # User limits (adjusted for 10k concurrent users)
            "limit_per_minute": 2,      # 2 requests per minute per user (2000/1000 users with buffer)
            "limit_per_hour": 60,       # 60 requests per hour per user
            "limit_per_day": 300,       # 300 requests per day per user
            "window": 60,
            "namespace": "user",
            "max_tokens_per_minute": 4000,  # 4k tokens per minute per user (1% of total token limit)
            "max_tokens_per_day": 100000    # 100k tokens per day per user
        },
        "ip": {
            "limit_per_minute": 10,     # 10 requests per minute per IP
            "limit_per_hour": 200,      # 200 requests per hour per IP
            "limit_per_day": 500,       # 500 requests per day per IP
            "window": 60,
            "namespace": "ip"
        }
    }
    
    # Token Management
    TOKEN_LIMITS = {
        "max_total_tokens_per_minute": 4000000,  # Gemini's 4M tokens per minute limit
        "max_tokens_per_request": 30000,         # Max tokens per single request
        "token_bucket_refill_rate": 100         # Tokens added per second to user's bucket
    }
    
    # Queue and Concurrency Settings
    QUEUE_CONFIG = {
        "max_queue_size": 5000,         # Increased queue size for concurrent users
        "queue_timeout": 30,            # Seconds to wait in queue
        "retry_delay": 5,               # Seconds to wait before retry
        "max_retries": 3,              # Maximum retry attempts
        "concurrent_request_limit": 100  # Maximum concurrent requests processing
    }
    
    # Load Balancing Settings
    LOAD_BALANCING = {
        "enabled": True,
        "algorithm": "round_robin",
        "max_requests_in_flight": 1900,  # Match global rate limit
        "request_timeout": 15           # Seconds before request times out
    }
    
    # Performance Settings 
    CHUNK_SIZE = 2000
    CHUNK_OVERLAP = 200
    MAX_CONCURRENT_REQUESTS = 100
    
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
        return cls.DIFFICULTY_LEVELS.get(difficulty, cls.DIFFICULTY_LEVELS["beginner"])["prompt"] 