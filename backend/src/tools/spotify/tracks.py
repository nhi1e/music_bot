"""
Spotify tools for track-related operations
"""

from langchain_core.tools import tool
from .base import get_spotify_client

@tool
def get_top_tracks(time_range: str = "medium_term", limit: int = 10) -> str:
    """Get user's TOP/MOST LISTENED TO tracks from Spotify. Use this for queries about "top tracks", "favorite tracks", "most played tracks", or "best tracks".
    
    This returns the user's most frequently played tracks over a time period, NOT recently played tracks.
    
    Args:
        time_range: Time period for top tracks ('short_term'=last 4 weeks, 'medium_term'=last 6 months, 'long_term'=all time)
        limit: Number of tracks to return (1-50)
    """
    try:
        sp = get_spotify_client()
        results = sp.current_user_top_tracks(limit=limit, time_range=time_range)
        
        if not results['items']:
            return "No top tracks found."
        
        tracks = []
        image_urls = []
        for idx, track in enumerate(results['items'], 1):
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            tracks.append(f"{idx}. {track['name']} by {artist_names}")
            
            # Add album image URL if available
            if track['album']['images'] and len(track['album']['images']) > 0:
                image_url = track['album']['images'][0]['url']  # Get the largest image
                image_urls.append(f"![Track: {track['name']}]({image_url})")
        
        time_period = {
            'short_term': 'last 4 weeks',
            'medium_term': 'last 6 months', 
            'long_term': 'all time'
        }.get(time_range, time_range)
        
        response = f"Your top {len(tracks)} tracks ({time_period}):\n" + "\n".join(tracks)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])  # Limit to 5 images
        
        return response
        
    except Exception as e:
        return f"Error fetching top tracks: {str(e)}"

@tool
def get_recently_played(limit: int = 10) -> str:
    """Get user's RECENTLY PLAYED tracks from Spotify (chronological order by play time). Use this ONLY for queries specifically asking about "recently played", "last played", or "what did I listen to recently".
    
    This returns tracks in the order they were played, NOT the most frequently played tracks.
    
    Args:
        limit: Number of recent tracks to return (1-50)
    """
    try:
        sp = get_spotify_client()
        results = sp.current_user_recently_played(limit=limit)
        
        if not results['items']:
            return "No recently played tracks found."
        
        tracks = []
        image_urls = []
        for idx, item in enumerate(results['items'], 1):
            track = item['track']
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            played_at = item['played_at'][:10]  # Just the date
            tracks.append(f"{idx}. {track['name']} by {artist_names} (played on {played_at})")
            
            # Add album image URL if available
            if track['album']['images'] and len(track['album']['images']) > 0 and len(image_urls) < 5:
                image_url = track['album']['images'][0]['url']  # Get the largest image
                image_urls.append(f"![Track: {track['name']}]({image_url})")
        
        response = f"Your {len(tracks)} recently played tracks:\n" + "\n".join(tracks)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])  # Limit to 5 images
        
        return response
        
    except Exception as e:
        return f"Error fetching recently played tracks: {str(e)}"

@tool
def search_tracks(query: str, limit: int = 10) -> str:
    """Search for tracks on Spotify.
    
    Args:
        query: Search query for tracks
        limit: Number of search results to return (1-50)
    """
    try:
        sp = get_spotify_client()
        results = sp.search(q=query, type='track', limit=limit)
        
        if not results['tracks']['items']:
            return f"No tracks found for '{query}'."
        
        tracks = []
        image_urls = []
        for idx, track in enumerate(results['tracks']['items'], 1):
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            album_name = track['album']['name']
            tracks.append(f"{idx}. {track['name']} by {artist_names} (from {album_name})")
            
            # Add album image URL if available
            if track['album']['images'] and len(track['album']['images']) > 0:
                image_url = track['album']['images'][0]['url']  # Get the largest image
                image_urls.append(f"![Track: {track['name']}]({image_url})")
        
        response = f"Search results for '{query}':\n" + "\n".join(tracks)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])  # Limit to 5 images
        
        return response
        
    except Exception as e:
        return f"Error searching tracks: {str(e)}"

@tool
def get_saved_tracks(limit: int = 20) -> str:
    """Get user's saved/liked tracks from Spotify.
    
    Args:
        limit: Number of saved tracks to return (1-50)
    """
    try:
        sp = get_spotify_client()
        results = sp.current_user_saved_tracks(limit=limit)
        
        if not results['items']:
            return "No saved tracks found."
        
        tracks = []
        image_urls = []
        for idx, item in enumerate(results['items'], 1):
            track = item['track']
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            tracks.append(f"{idx}. {track['name']} by {artist_names}")
            
            # Add album image URL if available
            if track['album']['images'] and len(track['album']['images']) > 0 and len(image_urls) < 5:
                image_url = track['album']['images'][0]['url']
                image_urls.append(f"![Track: {track['name']}]({image_url})")
        
        response = f"Your {len(tracks)} saved tracks:\n" + "\n".join(tracks)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])
        
        return response
        
    except Exception as e:
        return f"Error fetching saved tracks: {str(e)}"
