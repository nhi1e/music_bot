"""
Base Spotify client configuration and authentication
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_spotify_client():
    """Get authenticated Spotify client"""
    scope = "user-top-read playlist-read-private user-read-recently-played user-library-read user-follow-read user-follow-modify playlist-modify-public playlist-modify-private user-read-private"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope=scope,
        cache_path=".spotify_cache"
    ))
    return sp
