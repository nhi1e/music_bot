from langchain_core.tools import tool
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Spotify API setup
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
def get_playlist_names() -> str:
    """Get names of user's playlists."""
    try:
        sp = get_spotify_client()
        results = sp.current_user_playlists(limit=50)
        
        if not results['items']:
            return "No playlists found."
        
        playlists = []
        image_urls = []
        for playlist in results['items']:
            track_count = playlist['tracks']['total']
            playlists.append(f"• {playlist['name']} ({track_count} tracks)")
            
            # Add playlist image if available
            if playlist['images'] and len(playlist['images']) > 0 and len(image_urls) < 5:
                image_url = playlist['images'][0]['url']
                image_urls.append(f"![Playlist: {playlist['name']}]({image_url})")
        
        response = f"Your playlists:\n" + "\n".join(playlists)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])  # Limit to 5 images
        
        return response
        
    except Exception as e:
        return f"Error fetching playlists: {str(e)}"

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

@tool
def get_playlists_with_details(limit: int = 50) -> str:
    """Get user's playlists with creation details and track counts.
    
    Args:
        limit: Number of playlists to return (1-50)
    """
    try:
        sp = get_spotify_client()
        results = sp.current_user_playlists(limit=limit)
        
        if not results['items']:
            return "No playlists found."
        
        playlists = []
        image_urls = []
        for playlist in results['items']:
            # Get more detailed playlist info
            playlist_details = sp.playlist(playlist['id'])
            
            track_count = playlist['tracks']['total']
            owner = playlist['owner']['display_name']
            is_public = "Public" if playlist['public'] else "Private"
            
            # Extract creation info from description or use available data
            description = playlist.get('description', 'No description')
            if len(description) > 50:
                description = description[:50] + "..."
            
            playlists.append(
                f"• **{playlist['name']}** ({track_count} tracks)\n"
                f"  - Owner: {owner} | {is_public}\n"
                f"  - ID: {playlist['id']}\n"
                f"  - Description: {description}"
            )
            
            # Add playlist image if available
            if playlist['images'] and len(playlist['images']) > 0 and len(image_urls) < 5:
                image_url = playlist['images'][0]['url']
                image_urls.append(f"![Playlist: {playlist['name']}]({image_url})")
        
        response = f"Your {len(playlists)} playlists with details:\n\n" + "\n\n".join(playlists)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])
        
        return response
        
    except Exception as e:
        return f"Error fetching playlist details: {str(e)}"

@tool
def get_playlist_tracks(playlist_name: str = "", playlist_id: str = "", limit: int = 50) -> str:
    """Get tracks from a specific playlist by name or ID.
    
    Args:
        playlist_name: Name of the playlist to search for
        playlist_id: Spotify ID of the playlist (more precise than name)
        limit: Number of tracks to return (1-100)
    """
    try:
        sp = get_spotify_client()
        
        target_playlist_id = playlist_id
        matched_playlist_name = ""
        
        # If no ID provided, search by name
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            # Find playlist by name (case-insensitive partial match)
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    matched_playlist_name = playlist['name']
                    break
            
            if not target_playlist_id:
                # Try to find similar playlist names
                similar_playlists = []
                for playlist in playlists['items'][:10]:  # Check first 10 playlists
                    similar_playlists.append(f"• {playlist['name']}")
                
                if similar_playlists:
                    return (f"No playlist found matching '{playlist_name}'. "
                           f"Here are some of your playlists:\n" + "\n".join(similar_playlists) + 
                           f"\n\nTry using the exact playlist name or use get_playlists_with_details to see all playlists with their IDs.")
                else:
                    return f"No playlist found matching '{playlist_name}' and no playlists available to suggest."
        
        if not target_playlist_id:
            return "Please provide either playlist_name or playlist_id to search for tracks."
        
        # Get playlist details and tracks
        try:
            playlist_info = sp.playlist(target_playlist_id)
        except Exception as e:
            if "not found" in str(e).lower():
                return f"Playlist with ID '{target_playlist_id}' was not found. It may have been deleted or you may not have access to it."
            else:
                return f"Error accessing playlist: {str(e)}"
                
        tracks_result = sp.playlist_tracks(target_playlist_id, limit=limit)
        
        if not tracks_result['items']:
            return f"The playlist '{playlist_info['name']}' exists but contains no tracks."
        
        tracks = []
        image_urls = []
        valid_tracks = 0
        for idx, item in enumerate(tracks_result['items'], 1):
            if item['track'] and item['track']['name']:  # Some tracks might be None
                track = item['track']
                artist_names = ', '.join([artist['name'] for artist in track['artists']])
                album_name = track['album']['name']
                
                # Add album image URL if available
                if track['album']['images'] and len(track['album']['images']) > 0 and len(image_urls) < 5:
                    image_url = track['album']['images'][0]['url']
                    image_urls.append(f"![Track: {track['name']}]({image_url})")
                
                # Get date added if available
                added_at = item.get('added_at', '')
                if added_at:
                    added_date = added_at[:10]  # Just the date
                    tracks.append(f"{valid_tracks + 1}. {track['name']} by {artist_names}")
                    tracks.append(f"    From: {album_name} | Added: {added_date}")
                else:
                    tracks.append(f"{valid_tracks + 1}. {track['name']} by {artist_names} (from {album_name})")
                valid_tracks += 1
        
        if valid_tracks == 0:
            return f"The playlist '{playlist_info['name']}' contains tracks, but none could be retrieved properly."
        
        playlist_details = (
            f"**{playlist_info['name']}** by {playlist_info['owner']['display_name']}\n"
            f"Total tracks: {playlist_info['tracks']['total']} | "
            f"Followers: {playlist_info['followers']['total']}\n"
        )
        
        if playlist_info.get('description'):
            playlist_details += f"Description: {playlist_info['description']}\n"
        
        response = f"{playlist_details}\n**Tracks (showing {valid_tracks}):**\n" + "\n".join(tracks)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls[:5])  # Limit to 5 images
        
        return response
        
    except Exception as e:
        error_msg = f"Error fetching playlist tracks: {str(e)}"
        print(f"Playlist tracks error: {error_msg}")
        return error_msg

@tool
def get_recent_playlists(days_back: int = 30) -> str:
    """Get playlists that were likely created recently (approximate based on available data).
    
    Args:
        days_back: Number of days to look back (approximate)
    """
    try:
        sp = get_spotify_client()
        current_user = sp.current_user()
        user_id = current_user['id']
        
        # Get all user playlists
        all_playlists = []
        results = sp.current_user_playlists(limit=50)
        all_playlists.extend(results['items'])
        
        # Get more playlists if available
        while results['next']:
            results = sp.next(results)
            all_playlists.extend(results['items'])
        
        # Filter playlists owned by the user
        owned_playlists = [p for p in all_playlists if p['owner']['id'] == user_id]
        
        if not owned_playlists:
            return "No playlists found that you own."
        
        # Since Spotify API doesn't provide creation date directly,
        # we'll show the most recently modified playlists
        recent_playlists = []
        for playlist in owned_playlists[:20]:  # Check first 20 owned playlists
            try:
                # Get detailed playlist info
                detailed = sp.playlist(playlist['id'])
                track_count = detailed['tracks']['total']
                
                # Get a few recent tracks to estimate activity
                if track_count > 0:
                    tracks = sp.playlist_tracks(playlist['id'], limit=5)
                    recent_additions = []
                    
                    for item in tracks['items']:
                        if item.get('added_at'):
                            recent_additions.append(item['added_at'])
                    
                    if recent_additions:
                        latest_addition = max(recent_additions)
                        recent_playlists.append({
                            'name': playlist['name'],
                            'id': playlist['id'],
                            'tracks': track_count,
                            'latest_addition': latest_addition,
                            'description': detailed.get('description', 'No description')
                        })
            except:
                continue  # Skip if there's an error with this playlist
        
        # Sort by latest addition date
        recent_playlists.sort(key=lambda x: x['latest_addition'], reverse=True)
        
        if not recent_playlists:
            return f"No recent playlist activity found in the last {days_back} days."
        
        # Take top playlists (most recent activity)
        result_playlists = recent_playlists[:10]
        
        playlist_list = []
        for playlist in result_playlists:
            latest_date = playlist['latest_addition'][:10]
            description = playlist['description']
            if len(description) > 50:
                description = description[:50] + "..."
            
            playlist_list.append(
                f"• **{playlist['name']}** ({playlist['tracks']} tracks)\n"
                f"  - Latest activity: {latest_date}\n"
                f"  - ID: {playlist['id']}\n"
                f"  - Description: {description}"
            )
        
        return f"Your {len(result_playlists)} most recently active playlists:\n\n" + "\n\n".join(playlist_list)
        
    except Exception as e:
        return f"Error fetching recent playlists: {str(e)}"

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
def get_spotify_generated_playlists() -> str:
    """Get Spotify's automatically generated playlists like Discover Weekly, Release Radar, etc."""
    try:
        sp = get_spotify_client()
        
        # Get all playlists including Spotify-generated ones
        all_playlists = []
        results = sp.current_user_playlists(limit=50)
        all_playlists.extend(results['items'])
        
        # Get more playlists if available
        while results['next']:
            results = sp.next(results)
            all_playlists.extend(results['items'])
        
        # Filter for Spotify-generated playlists
        spotify_playlists = []
        spotify_generated_names = [
            'discover weekly', 'release radar', 'daily mix', 'on repeat', 
            'repeat rewind', 'wrapped', 'daylist', 'blend'
        ]
        
        for playlist in all_playlists:
            playlist_name_lower = playlist['name'].lower()
            if (playlist['owner']['id'] == 'spotify' or 
                any(gen_name in playlist_name_lower for gen_name in spotify_generated_names)):
                
                track_count = playlist['tracks']['total']
                spotify_playlists.append({
                    'name': playlist['name'],
                    'id': playlist['id'],
                    'tracks': track_count,
                    'owner': playlist['owner']['display_name']
                })
        
        if not spotify_playlists:
            return "No Spotify-generated playlists found. These playlists are usually created automatically by Spotify."
        
        playlist_list = []
        for playlist in spotify_playlists[:15]:  # Show up to 15 playlists
            playlist_list.append(
                f"• **{playlist['name']}** ({playlist['tracks']} tracks)\n"
                f"  - Created by: {playlist['owner']}\n"
                f"  - ID: {playlist['id']}"
            )
        
        return f"Your Spotify-generated playlists:\n\n" + "\n\n".join(playlist_list)
        
    except Exception as e:
        error_msg = f"Error fetching Spotify-generated playlists: {str(e)}"
        print(f"Spotify playlists error: {error_msg}")
        return error_msg

@tool
def get_current_user_profile() -> str:
    """Get current user's Spotify profile information."""
    try:
        sp = get_spotify_client()
        user = sp.current_user()
        
        profile_info = []
        image_urls = []
        
        profile_info.append(f"**{user.get('display_name', 'No display name')}** (@{user['id']})")
        profile_info.append(f"Followers: {user['followers']['total']:,}")
        
        if user.get('country'):
            profile_info.append(f"Country: {user['country']}")
        
        if user.get('product'):
            profile_info.append(f"Subscription: {user['product'].title()}")
        
        if user.get('external_urls', {}).get('spotify'):
            profile_info.append(f"Profile URL: {user['external_urls']['spotify']}")
            
        # Add user profile image if available
        if user.get('images') and len(user['images']) > 0:
            image_url = user['images'][0]['url']
            image_urls.append(f"![Profile: {user.get('display_name', user['id'])}]({image_url})")
        
        response = "\n".join(profile_info)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls)
        
        return response
        
    except Exception as e:
        error_msg = f"Error fetching user profile: {str(e)}"
        print(f"Profile error: {error_msg}")
        return error_msg

@tool
def get_user_profile(user_id: str) -> str:
    """Get another user's Spotify profile information.
    
    Args:
        user_id: Spotify user ID to look up
    """
    try:
        sp = get_spotify_client()
        user = sp.user(user_id)
        
        profile_info = []
        image_urls = []
        
        profile_info.append(f"**{user.get('display_name', 'No display name')}** (@{user['id']})")
        profile_info.append(f"Followers: {user['followers']['total']:,}")
        
        if user.get('external_urls', {}).get('spotify'):
            profile_info.append(f"Profile URL: {user['external_urls']['spotify']}")
            
        # Add user profile image if available
        if user.get('images') and len(user['images']) > 0:
            image_url = user['images'][0]['url']
            image_urls.append(f"![Profile: {user.get('display_name', user['id'])}]({image_url})")
        
        response = "\n".join(profile_info)
        if image_urls:
            response += "\n\n" + "\n".join(image_urls)
        
        return response
        
    except Exception as e:
        error_msg = f"Error fetching user profile for '{user_id}': {str(e)}"
        print(f"User profile error: {error_msg}")
        return error_msg

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

@tool
def follow_playlist(playlist_id: str = "", playlist_name: str = "") -> str:
    """Follow a playlist on Spotify.
    
    Args:
        playlist_id: Spotify ID of the playlist to follow
        playlist_name: Name of the playlist to search for and follow
    """
    try:
        sp = get_spotify_client()
        
        target_playlist_id = playlist_id
        
        # If no ID provided, search by name in user's playlists
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    break
            
            if not target_playlist_id:
                return f"No playlist found matching '{playlist_name}'."
        
        if not target_playlist_id:
            return "Please provide either playlist_id or playlist_name."
        
        # Get playlist info
        playlist_info = sp.playlist(target_playlist_id)
        
        # Follow the playlist
        sp.current_user_follow_playlist(target_playlist_id)
        
        return f"Successfully followed playlist **{playlist_info['name']}** by {playlist_info['owner']['display_name']}! 🎵"
        
    except Exception as e:
        error_msg = f"Error following playlist: {str(e)}"
        print(f"Follow playlist error: {error_msg}")
        return error_msg

@tool
def unfollow_playlist(playlist_id: str = "", playlist_name: str = "") -> str:
    """Unfollow a playlist on Spotify.
    
    Args:
        playlist_id: Spotify ID of the playlist to unfollow
        playlist_name: Name of the playlist to search for and unfollow
    """
    try:
        sp = get_spotify_client()
        
        target_playlist_id = playlist_id
        
        # If no ID provided, search by name in user's playlists
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    break
            
            if not target_playlist_id:
                return f"No playlist found matching '{playlist_name}'."
        
        if not target_playlist_id:
            return "Please provide either playlist_id or playlist_name."
        
        # Get playlist info
        playlist_info = sp.playlist(target_playlist_id)
        
        # Unfollow the playlist
        sp.current_user_unfollow_playlist(target_playlist_id)
        
        return f"Successfully unfollowed playlist **{playlist_info['name']}**."
        
    except Exception as e:
        error_msg = f"Error unfollowing playlist: {str(e)}"
        print(f"Unfollow playlist error: {error_msg}")
        return error_msg

@tool
def check_if_following_playlist(playlist_id: str = "", playlist_name: str = "") -> str:
    """Check if the current user follows a specific playlist.
    
    Args:
        playlist_id: Spotify ID of the playlist to check
        playlist_name: Name of the playlist to search for and check
    """
    try:
        sp = get_spotify_client()
        current_user = sp.current_user()
        user_id = current_user['id']
        
        target_playlist_id = playlist_id
        
        # If no ID provided, search by name
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    break
            
            if not target_playlist_id:
                return f"No playlist found matching '{playlist_name}'."
        
        if not target_playlist_id:
            return "Please provide either playlist_id or playlist_name."
        
        # Get playlist info
        playlist_info = sp.playlist(target_playlist_id)
        
        # Check if following
        is_following = sp.playlist_is_following(target_playlist_id, [user_id])[0]
        
        if is_following:
            return f"Yes! You're following playlist **{playlist_info['name']}** by {playlist_info['owner']['display_name']} 🎵"
        else:
            return f"No, you're not following playlist **{playlist_info['name']}** yet."
        
    except Exception as e:
        error_msg = f"Error checking playlist follow status: {str(e)}"
        print(f"Check playlist follow error: {error_msg}")
        return error_msg

@tool
def get_recommendations_by_track(track_name: str, artist_name: str, limit: int = 10) -> str:
    """Get Spotify recommendations based on a specific track and artist.
    
    Use this tool when a user asks for songs similar to a specific track that's not found 
    in the local database. This searches Spotify for the track and uses alternative methods
    to find similar music.
    
    Args:
        track_name: Name of the seed track
        artist_name: Name of the seed artist  
        limit: Number of recommendations to return (1-50)
    """
    try:
        sp = get_spotify_client()
        
        # First, search for the seed track on Spotify
        search_query = f"track:{track_name} artist:{artist_name}"
        search_results = sp.search(q=search_query, type='track', limit=1)
        
        if not search_results['tracks']['items']:
            # Try a broader search without field restrictions
            search_query = f"{track_name} {artist_name}"
            search_results = sp.search(q=search_query, type='track', limit=1)
            
            if not search_results['tracks']['items']:
                return f"Could not find '{track_name}' by '{artist_name}' on Spotify."
        
        seed_track = search_results['tracks']['items'][0]
        seed_track_id = seed_track['id']
        seed_artist_id = seed_track['artists'][0]['id']
        
        result = f"🎵 **Recommendations based on '{track_name}' by '{artist_name}':**\n\n"
        result += f"**Found:** {seed_track['name']} by {seed_track['artists'][0]['name']}\n\n"
        
        recommendations = []
        
        # Strategy 1: Try Spotify recommendations API
        try:
            spotify_recs = sp.recommendations(seed_tracks=[seed_track_id], limit=limit)
            if spotify_recs['tracks']:
                recommendations = spotify_recs['tracks']
                result += "📈 **Spotify Algorithm Recommendations:**\n"
        except:
            # Strategy 2: Get related artists and their top tracks
            try:
                related_artists = sp.artist_related_artists(seed_artist_id)
                if related_artists['artists']:
                    result += "🎯 **Similar Artists' Popular Tracks:**\n"
                    for artist in related_artists['artists'][:3]:  # Top 3 related artists
                        top_tracks = sp.artist_top_tracks(artist['id'])
                        for track in top_tracks['tracks'][:3]:  # Top 3 tracks per artist
                            recommendations.append(track)
                            if len(recommendations) >= limit:
                                break
                        if len(recommendations) >= limit:
                            break
            except:
                # Strategy 3: Search for similar tracks by genre/style
                try:
                    # Get audio features of the seed track
                    audio_features = sp.audio_features([seed_track_id])[0]
                    if audio_features:
                        # Search for tracks with similar characteristics
                        danceability = audio_features['danceability']
                        energy = audio_features['energy']
                        valence = audio_features['valence']
                        
                        # Build search query based on audio characteristics
                        mood = "happy" if valence > 0.6 else "sad" if valence < 0.4 else "chill"
                        energy_level = "high energy" if energy > 0.7 else "low energy" if energy < 0.3 else "medium energy"
                        
                        search_query = f"{mood} {energy_level} music"
                        similar_search = sp.search(q=search_query, type='track', limit=limit)
                        recommendations = similar_search['tracks']['items']
                        result += f"🎭 **Tracks with similar vibe ({mood}, {energy_level}):**\n"
                except:
                    # Strategy 4: Fallback to artist's other tracks
                    artist_albums = sp.artist_albums(seed_artist_id, album_type='album,single', limit=5)
                    for album in artist_albums['items']:
                        album_tracks = sp.album_tracks(album['id'])
                        for track in album_tracks['items']:
                            if track['name'].lower() != seed_track['name'].lower():
                                recommendations.append(track)
                                if len(recommendations) >= limit:
                                    break
                        if len(recommendations) >= limit:
                            break
                    result += f"� **More from {artist_name}:**\n"
        
        if not recommendations:
            return f"Could not find similar recommendations for '{track_name}' by '{artist_name}'. The track exists on Spotify but recommendations are not available."
        
        # Format the results
        for idx, track in enumerate(recommendations[:limit], 1):
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            result += f"{idx}. **{track['name']}** by {artist_names}\n"
            
            # Try to get audio features for context
            try:
                audio_features = sp.audio_features([track['id']])[0]
                if audio_features:
                    danceability = round(audio_features['danceability'], 2)
                    energy = round(audio_features['energy'], 2)
                    valence = round(audio_features['valence'], 2)
                    tempo = round(audio_features['tempo'])
                    
                    result += f"   🎭 Vibe: {'Upbeat' if valence > 0.6 else 'Chill' if valence > 0.4 else 'Mellow'} | "
                    result += f"⚡ Energy: {energy} | 💃 Danceability: {danceability} | 🥁 Tempo: {tempo} BPM\n"
            except:
                pass
                
            if track.get('preview_url'):
                result += f"   🎧 [Preview]({track['preview_url']})\n"
            result += "\n"
        
        result += f"\n🎯 Found {len(recommendations[:limit])} similar tracks using Spotify's music database."
        
        return result
        
    except Exception as e:
        error_msg = f"Error getting Spotify recommendations: {str(e)}"
        print(f"Spotify recommendation error: {error_msg}")
        return error_msg

@tool  
def get_recommendations_by_audio_features(danceability: float = None, energy: float = None, 
                                        valence: float = None, tempo: float = None,
                                        acousticness: float = None, instrumentalness: float = None,
                                        limit: int = 10) -> str:
    """Get Spotify recommendations based on specific audio characteristics.
    
    Use this for getting recommendations based on desired musical attributes when 
    no specific seed track is available.
    
    Args:
        danceability: Target danceability (0.0-1.0)
        energy: Target energy level (0.0-1.0)  
        valence: Target mood/positivity (0.0-1.0, higher = more positive)
        tempo: Target tempo in BPM
        acousticness: Target acousticness (0.0-1.0)
        instrumentalness: Target instrumentalness (0.0-1.0)
        limit: Number of recommendations (1-100)
    """
    try:
        sp = get_spotify_client()
        
        # Build target audio features dict
        target_features = {}
        if danceability is not None:
            target_features['target_danceability'] = max(0.0, min(1.0, danceability))
        if energy is not None:
            target_features['target_energy'] = max(0.0, min(1.0, energy))
        if valence is not None:
            target_features['target_valence'] = max(0.0, min(1.0, valence))
        if tempo is not None:
            target_features['target_tempo'] = max(50, min(200, tempo))
        if acousticness is not None:
            target_features['target_acousticness'] = max(0.0, min(1.0, acousticness))
        if instrumentalness is not None:
            target_features['target_instrumentalness'] = max(0.0, min(1.0, instrumentalness))
        
        # Need at least one seed - use popular genres as backup
        recommendations = sp.recommendations(
            seed_genres=['pop', 'indie'],
            limit=limit,
            **target_features
        )
        
        if not recommendations['tracks']:
            return "No recommendations found for the specified audio features."
        
        # Format results
        feature_desc = []
        if danceability is not None:
            feature_desc.append(f"Danceability: {danceability}")
        if energy is not None:
            feature_desc.append(f"Energy: {energy}")
        if valence is not None:
            feature_desc.append(f"Mood: {valence}")
        if tempo is not None:
            feature_desc.append(f"Tempo: {tempo} BPM")
            
        result = f"🎵 **Spotify Recommendations for audio features:** {', '.join(feature_desc)}\n\n"
        
        for idx, track in enumerate(recommendations['tracks'], 1):
            artist_names = ', '.join([artist['name'] for artist in track['artists']])
            result += f"{idx}. **{track['name']}** by {artist_names}\n"
            
            if track['preview_url']:
                result += f"   🎧 [Preview]({track['preview_url']})\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        error_msg = f"Error getting audio feature recommendations: {str(e)}"
        print(f"Audio feature recommendation error: {error_msg}")
        return error_msg

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
