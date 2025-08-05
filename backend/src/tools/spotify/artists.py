"""
Spotify tools for artist-related operations
"""

from langchain_core.tools import tool
from .base import get_spotify_client

@tool
def get_top_artists(time_range: str = "medium_term", limit: int = 10) -> str:
    """Get user's top artists from Spotify.
    
    Args:
        time_range: Time period for top artists ('short_term', 'medium_term', 'long_term')
        limit: Number of artists to return (1-50)
    """
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
        
        time_period = {
            'short_term': 'last 4 weeks',
            'medium_term': 'last 6 months', 
            'long_term': 'all time'
        }.get(time_range, time_range)
        
        response = f"Here are your top {len(artists)} artists from the {time_period}:\n\n" + "\n".join(artists)
        
        # Add images for top 5 artists
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])
        
        response += "\n\nQuite an eclectic mix of genres and styles! 🎧 Any artist here you'd like to delve deeper into or find similar recommendations for?"
        
        return response
        
    except Exception as e:
        return f"Error fetching top artists: {str(e)}"

@tool
def search_artist_info(artist_name: str) -> str:
    """Search for artist information on Spotify including top tracks and albums.
    
    Args:
        artist_name: Name of the artist to search for
    """
    try:
        sp = get_spotify_client()
        
        # Search for the artist
        results = sp.search(q=artist_name, type='artist', limit=5)
        
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'."
        
        artist = results['artists']['items'][0]  # Get the first (most relevant) result
        artist_id = artist['id']
        
        # Get artist details
        artist_info = []
        image_urls = []
        
        artist_info.append(f"**{artist['name']}**")
        artist_info.append(f"Followers: {artist['followers']['total']:,}")
        artist_info.append(f"Popularity: {artist['popularity']}/100")
        
        if artist['genres']:
            artist_info.append(f"Genres: {', '.join(artist['genres'])}")
        
        # Add artist image
        if artist['images'] and len(artist['images']) > 0:
            image_url = artist['images'][0]['url']
            image_urls.append(f"![Artist: {artist['name']}]({image_url})")
        
        # Get top tracks
        top_tracks = sp.artist_top_tracks(artist_id, country='US')
        if top_tracks['tracks']:
            artist_info.append(f"\n**Top Tracks:**")
            for idx, track in enumerate(top_tracks['tracks'][:5], 1):
                artist_info.append(f"{idx}. {track['name']} (from {track['album']['name']})")
                
                # Add album images from top tracks
                if track['album']['images'] and len(track['album']['images']) > 0 and len(image_urls) < 5:
                    image_url = track['album']['images'][0]['url']
                    image_urls.append(f"![Album: {track['album']['name']}]({image_url})")
        
        # Get albums
        albums = sp.artist_albums(artist_id, album_type='album', limit=5)
        if albums['items']:
            artist_info.append(f"\n**Recent Albums:**")
            for album in albums['items']:
                release_date = album.get('release_date', 'Unknown')
                artist_info.append(f"• {album['name']} ({release_date})")
                
                # Add album images
                if album['images'] and len(album['images']) > 0 and len(image_urls) < 5:
                    image_url = album['images'][0]['url']
                    image_urls.append(f"![Album: {album['name']}]({image_url})")
        
        response = "\n".join(artist_info)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])
        
        return response
        
    except Exception as e:
        return f"Error searching for artist: {str(e)}"

@tool
def get_followed_artists(limit: int = 20) -> str:
    """Get artists that the current user follows.
    
    Args:
        limit: Number of followed artists to return (1-50)
    """
    try:
        sp = get_spotify_client()
        results = sp.current_user_followed_artists(limit=limit)
        
        if not results['artists']['items']:
            return "You're not following any artists yet."
        
        artists = []
        image_urls = []
        for idx, artist in enumerate(results['artists']['items'], 1):
            followers = artist['followers']['total']
            genres = ', '.join(artist['genres'][:2]) if artist['genres'] else 'No genres listed'
            
            artists.append(
                f"{idx}. **{artist['name']}**\n"
                f"    - Followers: {followers:,}\n"
                f"    - Genres: {genres}"
            )
            
            # Add artist image if available
            if artist['images'] and len(artist['images']) > 0 and len(image_urls) < 5:
                image_url = artist['images'][0]['url']
                image_urls.append(f"![Artist: {artist['name']}]({image_url})")
        
        response = f"Artists you're following ({len(artists)} shown):\n\n" + "\n\n".join(artists)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])
        
        return response
        
    except Exception as e:
        error_msg = f"Error fetching followed artists: {str(e)}"
        print(f"Followed artists error: {error_msg}")
        return error_msg

@tool
def follow_artist(artist_name: str) -> str:
    """Follow an artist on Spotify.
    
    Args:
        artist_name: Name of the artist to follow
    """
    try:
        sp = get_spotify_client()
        
        # First, search for the artist
        results = sp.search(q=artist_name, type='artist', limit=1)
        
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'."
        
        artist = results['artists']['items'][0]
        artist_id = artist['id']
        
        # Follow the artist
        sp.user_follow_artists([artist_id])
        
        return f"Successfully followed **{artist['name']}**! 🎵"
        
    except Exception as e:
        error_msg = f"Error following artist '{artist_name}': {str(e)}"
        print(f"Follow artist error: {error_msg}")
        return error_msg

@tool
def unfollow_artist(artist_name: str) -> str:
    """Unfollow an artist on Spotify.
    
    Args:
        artist_name: Name of the artist to unfollow
    """
    try:
        sp = get_spotify_client()
        
        # First, search for the artist
        results = sp.search(q=artist_name, type='artist', limit=1)
        
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'."
        
        artist = results['artists']['items'][0]
        artist_id = artist['id']
        
        # Unfollow the artist
        sp.user_unfollow_artists([artist_id])
        
        return f"Successfully unfollowed **{artist['name']}**."
        
    except Exception as e:
        error_msg = f"Error unfollowing artist '{artist_name}': {str(e)}"
        print(f"Unfollow artist error: {error_msg}")
        return error_msg

@tool
def check_if_following_artist(artist_name: str) -> str:
    """Check if the current user follows a specific artist.
    
    Args:
        artist_name: Name of the artist to check
    """
    try:
        sp = get_spotify_client()
        
        # First, search for the artist
        results = sp.search(q=artist_name, type='artist', limit=1)
        
        if not results['artists']['items']:
            return f"No artist found for '{artist_name}'."
        
        artist = results['artists']['items'][0]
        artist_id = artist['id']
        
        # Check if following
        is_following = sp.current_user_following_artists([artist_id])[0]
        
        if is_following:
            return f"Yes! You're following **{artist['name']}** 🎵"
        else:
            return f"No, you're not following **{artist['name']}** yet."
        
    except Exception as e:
        error_msg = f"Error checking follow status for '{artist_name}': {str(e)}"
        print(f"Check follow error: {error_msg}")
        return error_msg
