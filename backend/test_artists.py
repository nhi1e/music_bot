#!/usr/bin/env python3

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

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

def test_get_top_artists(time_range: str = "medium_term", limit: int = 5) -> str:
    """Test version of get_top_artists with image URLs"""
    try:
        sp = get_spotify_client()
        results = sp.current_user_top_artists(limit=limit, time_range=time_range)
        
        if not results['items']:
            return "No top artists found."
        
        artists = []
        image_urls = []
        for idx, artist in enumerate(results['items'], 1):
            followers = artist['followers']['total']
            popularity = artist['popularity']
            genres = ', '.join(artist['genres'][:3]) if artist['genres'] else 'No genres listed'
            
            artists.append(
                f"{idx}. **{artist['name']}** - {genres if genres != 'No genres listed' else 'Popular and soulful, but no specific genres listed'}."
            )
            
            # Add artist image URL if available
            if artist['images'] and len(artist['images']) > 0:
                image_url = artist['images'][0]['url']  # Get the largest image
                image_urls.append(f"![Artist: {artist['name']}]({image_url})")
                print(f"Added image for {artist['name']}: {image_url}")
        
        time_period = {
            'short_term': 'last 4 weeks',
            'medium_term': 'last 6 months', 
            'long_term': 'all time'
        }.get(time_range, time_range)
        
        response = f"Here are your top {len(artists)} artists from the {time_period}:\n\n" + "\n".join(artists)
        
        # Add images for top 5 artists
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])
            print(f"Added {len(image_urls[:5])} images to response")
        
        response += "\n\nQuite an eclectic mix of genres and styles! 🎧 Any artist here you'd like to delve deeper into or find similar recommendations for?"
        
        return response
        
    except Exception as e:
        return f"Error fetching top artists: {str(e)}"

if __name__ == "__main__":
    print("Testing get_top_artists function...")
    result = test_get_top_artists()
    print("\n" + "="*50)
    print("RESULT:")
    print("="*50)
    print(result)
