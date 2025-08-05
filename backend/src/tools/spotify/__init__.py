"""
Modular Spotify tools organized by functionality.
Import all tools from their respective modules.
"""

# Track tools
from .tracks import (
    get_top_tracks,
    get_recently_played,
    search_tracks,
    get_saved_tracks
)

# Artist tools
from .artists import (
    get_top_artists,
    search_artist_info,
    get_followed_artists,
    follow_artist,
    unfollow_artist,
    check_if_following_artist
)

# Playlist tools
from .playlists import (
    get_playlist_names,
    get_playlists_with_details,
    get_playlist_tracks,
    get_recent_playlists,
    get_spotify_generated_playlists,
    follow_playlist,
    unfollow_playlist,
    check_if_following_playlist,
    create_playlist,
    add_track_to_playlist,
    remove_track_from_playlist,
    search_and_add_to_playlist
)

# User profile tools
from .user import (
    get_current_user_profile,
    get_user_profile
)

# Recommendation tools
from .recommendations import (
    get_recommendations_by_track,
    get_recommendations_by_audio_features
)

# Spotify Wrapped tools
from .wrapped import (
    generate_spotify_wrapped
)

# All available tools for easy importing
__all__ = [
    # Track tools
    'get_top_tracks',
    'get_recently_played', 
    'search_tracks',
    'get_saved_tracks',
    
    # Artist tools
    'get_top_artists',
    'search_artist_info',
    'get_followed_artists',
    'follow_artist',
    'unfollow_artist',
    'check_if_following_artist',
    
    # Playlist tools
    'get_playlist_names',
    'get_playlists_with_details',
    'get_playlist_tracks',
    'get_recent_playlists',
    'get_spotify_generated_playlists',
    'follow_playlist',
    'unfollow_playlist',
    'check_if_following_playlist',
    'create_playlist',
    'add_track_to_playlist',
    'remove_track_from_playlist',
    'search_and_add_to_playlist',
    
    # User tools
    'get_current_user_profile',
    'get_user_profile',
    
    # Recommendation tools
    'get_recommendations_by_track',
    'get_recommendations_by_audio_features',
    
    # Wrapped tools
    'generate_spotify_wrapped'
]
