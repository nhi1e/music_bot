"""
Spotify tools for playlist-related operations
"""

from langchain_core.tools import tool
from .base import get_spotify_client

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
def create_playlist(name: str, description: str = "", public: bool = False) -> str:
    """Create a new playlist for the current user.
    
    Args:
        name: Name of the new playlist
        description: Description for the playlist (optional)
        public: Whether the playlist should be public (default: False)
    """
    try:
        sp = get_spotify_client()
        user = sp.current_user()
        
        # Create the playlist
        playlist = sp.user_playlist_create(
            user=user['id'],
            name=name,
            public=public,
            description=description
        )
        
        return f"✅ Successfully created playlist **{name}**!\n- ID: {playlist['id']}\n- Public: {'Yes' if public else 'No'}\n- Description: {description if description else 'No description'}"
        
    except Exception as e:
        return f"Error creating playlist: {str(e)}"

@tool  
def add_track_to_playlist(playlist_name: str = "", playlist_id: str = "", track_name: str = "", artist_name: str = "") -> str:
    """Add a track to a specific playlist by searching for the track first.
    
    Args:
        playlist_name: Name of the playlist to add to
        playlist_id: Spotify ID of the playlist (more precise than name)
        track_name: Name of the track to add
        artist_name: Artist of the track to add (helps with accuracy)
    """
    try:
        sp = get_spotify_client()
        
        # Find the playlist
        target_playlist_id = playlist_id
        matched_playlist_name = ""
        
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            # Find playlist by name (case-insensitive partial match)
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    matched_playlist_name = playlist['name']
                    break
            
            if not target_playlist_id:
                return f"No playlist found matching '{playlist_name}'. Use get_playlist_names to see your playlists."
        
        if not target_playlist_id:
            return "Please provide either playlist_name or playlist_id."
        
        # Search for the track
        if not track_name:
            return "Please provide track_name to add to the playlist."
        
        search_query = f"track:{track_name}"
        if artist_name:
            search_query += f" artist:{artist_name}"
        
        search_results = sp.search(q=search_query, type='track', limit=5)
        
        if not search_results['tracks']['items']:
            # Try broader search
            search_query = f"{track_name}"
            if artist_name:
                search_query += f" {artist_name}"
            search_results = sp.search(q=search_query, type='track', limit=5)
            
            if not search_results['tracks']['items']:
                return f"Could not find track '{track_name}'{' by ' + artist_name if artist_name else ''} on Spotify."
        
        # Get the best match (first result)
        track = search_results['tracks']['items'][0]
        track_uri = track['uri']
        track_artists = ', '.join([artist['name'] for artist in track['artists']])
        
        # Add track to playlist
        sp.playlist_add_items(target_playlist_id, [track_uri])
        
        # Get playlist info for confirmation
        playlist_info = sp.playlist(target_playlist_id)
        
        return f"✅ Successfully added **{track['name']}** by **{track_artists}** to playlist **{playlist_info['name']}**!"
        
    except Exception as e:
        return f"Error adding track to playlist: {str(e)}"

@tool
def remove_track_from_playlist(playlist_name: str = "", playlist_id: str = "", track_name: str = "", artist_name: str = "") -> str:
    """Remove a track from a specific playlist.
    
    Args:
        playlist_name: Name of the playlist to remove from
        playlist_id: Spotify ID of the playlist (more precise than name)
        track_name: Name of the track to remove
        artist_name: Artist of the track to remove (helps with accuracy)
    """
    try:
        sp = get_spotify_client()
        
        # Find the playlist
        target_playlist_id = playlist_id
        
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    break
            
            if not target_playlist_id:
                return f"No playlist found matching '{playlist_name}'."
        
        if not target_playlist_id:
            return "Please provide either playlist_name or playlist_id."
        
        # Get playlist tracks to find the specific track to remove
        playlist_tracks = sp.playlist_tracks(target_playlist_id)
        
        track_to_remove = None
        for item in playlist_tracks['items']:
            if item['track'] and item['track']['name']:
                track = item['track']
                track_artists = [artist['name'].lower() for artist in track['artists']]
                
                # Match track name and optionally artist
                if track_name.lower() in track['name'].lower():
                    if not artist_name or any(artist_name.lower() in artist for artist in track_artists):
                        track_to_remove = track
                        break
        
        if not track_to_remove:
            return f"Could not find track '{track_name}'{' by ' + artist_name if artist_name else ''} in the playlist."
        
        # Remove the track
        sp.playlist_remove_all_occurrences_of_items(target_playlist_id, [track_to_remove['uri']])
        
        # Get playlist info for confirmation
        playlist_info = sp.playlist(target_playlist_id)
        track_artists = ', '.join([artist['name'] for artist in track_to_remove['artists']])
        
        return f"✅ Successfully removed **{track_to_remove['name']}** by **{track_artists}** from playlist **{playlist_info['name']}**!"
        
    except Exception as e:
        return f"Error removing track from playlist: {str(e)}"

@tool
def search_and_add_to_playlist(query: str, playlist_name: str = "", playlist_id: str = "") -> str:
    """Search for tracks and add the first result to a playlist. Useful for natural language requests.
    
    Args:
        query: Search query (e.g., "Jump by BlackPink", "Taylor Swift new song")
        playlist_name: Name of the playlist to add to
        playlist_id: Spotify ID of the playlist (more precise than name)
    """
    try:
        sp = get_spotify_client()
        
        # Find the playlist
        target_playlist_id = playlist_id
        
        if not target_playlist_id and playlist_name:
            playlists = sp.current_user_playlists(limit=50)
            
            for playlist in playlists['items']:
                if playlist_name.lower() in playlist['name'].lower():
                    target_playlist_id = playlist['id']
                    break
            
            if not target_playlist_id:
                return f"No playlist found matching '{playlist_name}'. Use get_playlist_names to see your playlists."
        
        if not target_playlist_id:
            return "Please provide either playlist_name or playlist_id."
        
        # Search for the track
        search_results = sp.search(q=query, type='track', limit=3)
        
        if not search_results['tracks']['items']:
            return f"Could not find any tracks matching '{query}' on Spotify."
        
        # Get the best match (first result)
        track = search_results['tracks']['items'][0]
        track_uri = track['uri']
        track_artists = ', '.join([artist['name'] for artist in track['artists']])
        
        # Add track to playlist
        sp.playlist_add_items(target_playlist_id, [track_uri])
        
        # Get playlist info for confirmation
        playlist_info = sp.playlist(target_playlist_id)
        
        return f"✅ Successfully added **{track['name']}** by **{track_artists}** to playlist **{playlist_info['name']}**!\n\n(Found from search: '{query}')"
        
    except Exception as e:
        return f"Error searching and adding track to playlist: {str(e)}"
