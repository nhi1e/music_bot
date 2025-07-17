# Configuration settings for the music recommendation bot
"""
Configuration module for managing environment variables and settings.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Spotify API Configuration
    SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
    SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
    SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Tavily Configuration
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    
    # Database Configuration
    DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data')
    DATASET_PATH = os.path.join(DATA_PATH, 'dataset.csv')
    
    # Cache Configuration
    SPOTIFY_CACHE_PATH = ".spotify_cache"
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ]
    
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set"""
        required_vars = [
            'SPOTIFY_CLIENT_ID',
            'SPOTIFY_CLIENT_SECRET', 
            'SPOTIFY_REDIRECT_URI',
            'OPENAI_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

# Create a global config instance
config = Config()
