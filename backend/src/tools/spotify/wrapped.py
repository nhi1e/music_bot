"""
Spotify tools for generating Spotify Wrapped summaries
"""

from langchain_core.tools import tool
import json
from .base import get_spotify_client

@tool
def generate_spotify_wrapped(time_range: str = "long_term") -> str:
    """Generate a Spotify Wrapped summary with top artists, songs, and genre data.
    Use this when user asks for 'Spotify Wrapped', 'year in review', 'music summary', or similar requests.
    
    Args:
        time_range: Time period ('short_term'=last 4 weeks, 'medium_term'=last 6 months, 'long_term'=all time)
    """
    try:
        sp = get_spotify_client()
        
        # Get top artists (5)
        top_artists_result = sp.current_user_top_artists(limit=5, time_range=time_range)
        artists = []
        for artist in top_artists_result['items']:
            artist_data = {
                "name": artist['name']
            }
            if artist['images'] and len(artist['images']) > 0:
                artist_data["image"] = artist['images'][0]['url']
            artists.append(artist_data)
        
        # Get top tracks (5)
        top_tracks_result = sp.current_user_top_tracks(limit=5, time_range=time_range)
        songs = []
        for track in top_tracks_result['items']:
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            songs.append({
                "name": track['name'],
                "artist": artist_names
            })
        
        # Determine top genre from artists
        all_genres = []
        for artist in top_artists_result['items']:
            all_genres.extend(artist['genres'])
        
        # Find most common genre
        genre_counts = {}
        for genre in all_genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        top_genre = "Alternative" # Default fallback
        if genre_counts:
            top_genre = max(genre_counts, key=genre_counts.get)
            # Format genre nicely
            top_genre = top_genre.title().replace('_', ' ')
        
        # Get timeframe label
        timeframe_labels = {
            'short_term': 'Last 4 Weeks',
            'medium_term': 'Last 6 Months', 
            'long_term': 'This Year'
        }
        timeframe = timeframe_labels.get(time_range, 'This Year')
        
        # Get top artist image
        top_artist_image = None
        if artists and artists[0].get('image'):
            top_artist_image = artists[0]['image']
        
        # Create the wrapped data
        wrapped_data = {
            "topArtists": artists,
            "topSongs": songs,
            "topGenre": top_genre,
            "timeframe": timeframe,
            "topArtistImage": top_artist_image
        }
        
        # Return as JSON string embedded in a response
        json_data = json.dumps(wrapped_data, indent=2)
        
        response = f"🎵 Here's your Spotify Wrapped for {timeframe.lower()}! 🎵\n\n"
        response += f"**Top Artists:**\n"
        for i, artist in enumerate(artists, 1):
            response += f"{i}. {artist['name']}\n"
        
        response += f"\n**Top Songs:**\n"
        for i, song in enumerate(songs, 1):
            response += f"{i}. {song['name']} by {song['artist']}\n"
        
        response += f"\n**Top Genre:** {top_genre}\n\n"
        response += f"SPOTIFY_WRAPPED_DATA:{json_data}"
        
        return response
        
    except Exception as e:
        return f"Error generating Spotify Wrapped: {str(e)}"
