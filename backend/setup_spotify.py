#!/usr/bin/env python3
"""
Setup script for Spotify API authentication.
Run this to test your Spotify API connection and authorize the app.
"""

import os
import sys
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

def setup_spotify():
    """Setup and test Spotify API connection"""
    
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'SPOTIFY_REDIRECT_URI']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your Spotify API credentials")
        print("3. Get credentials from: https://developer.spotify.com/dashboard")
        return False
    
    try:
        print("🔑 Setting up Spotify authentication...")
        
        scope = "user-top-read playlist-read-private user-read-recently-played user-library-read"
        
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.getenv('SPOTIFY_CLIENT_ID'),
            client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
            redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
            scope=scope,
            cache_path=".spotify_cache"
        ))
        
        # Test the connection
        print("🧪 Testing Spotify API connection...")
        user = sp.current_user()
        print(f"✅ Successfully connected to Spotify!")
        print(f"👤 Logged in as: {user['display_name']} ({user['id']})")
        
        # Test a few endpoints
        print("\n🎵 Testing API endpoints...")
        
        # Test top tracks
        try:
            top_tracks = sp.current_user_top_tracks(limit=3, time_range='short_term')
            print(f"✅ Top tracks: Found {len(top_tracks['items'])} tracks")
        except Exception as e:
            print(f"❌ Top tracks: {e}")
        
        # Test playlists
        try:
            playlists = sp.current_user_playlists(limit=3)
            print(f"✅ Playlists: Found {len(playlists['items'])} playlists")
        except Exception as e:
            print(f"❌ Playlists: {e}")
            
        # Test recently played
        try:
            recent = sp.current_user_recently_played(limit=3)
            print(f"✅ Recent tracks: Found {len(recent['items'])} tracks")
        except Exception as e:
            print(f"❌ Recent tracks: {e}")
        
        print("\n🎉 Spotify setup complete! You can now use the chatbot.")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up Spotify: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your Spotify API credentials")
        print("2. Make sure your redirect URI is registered in Spotify Dashboard")
        print("3. Ensure you have the correct scopes enabled")
        return False

if __name__ == "__main__":
    print("🎵 Spotify Music Chatbot Setup")
    print("=" * 40)
    
    if not os.path.exists('.env'):
        print("❌ No .env file found!")
        print("📝 Please copy .env.example to .env and fill in your credentials")
        sys.exit(1)
    
    success = setup_spotify()
    sys.exit(0 if success else 1)
