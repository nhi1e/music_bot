"""
Spotify tools for user profile operations
"""

from langchain_core.tools import tool
from .base import get_spotify_client

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
