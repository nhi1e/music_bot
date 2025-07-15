from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

app = FastAPI(title="Music Recommendation Bot API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Spotify OAuth setup
def get_spotify_oauth():
    """Get Spotify OAuth manager"""
    scope = "user-top-read playlist-read-private user-read-recently-played user-library-read user-follow-read user-follow-modify playlist-modify-public playlist-modify-private user-read-private"
    
    return SpotifyOAuth(
        client_id=os.getenv('SPOTIFY_CLIENT_ID'),
        client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
        scope=scope,
        cache_path=".spotify_cache"
    )

@app.get("/")
async def root():
    return {"message": "Music Recommendation Bot API", "status": "running"}

@app.get("/auth/spotify")
async def spotify_auth():
    """Initiate Spotify OAuth flow"""
    try:
        sp_oauth = get_spotify_oauth()
        auth_url = sp_oauth.get_authorize_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error initiating Spotify auth: {str(e)}")

@app.get("/callback")
async def spotify_callback(request: Request):
    """Handle Spotify OAuth callback"""
    try:
        sp_oauth = get_spotify_oauth()
        
        # Get the authorization code from the callback URL
        code = request.query_params.get("code")
        error = request.query_params.get("error")
        
        if error:
            # User denied access
            frontend_url = "http://localhost:3001"
            redirect_url = f"{frontend_url}?auth=denied"
            return RedirectResponse(url=redirect_url)
        
        if not code:
            raise HTTPException(status_code=400, detail="No authorization code received")
        
        # Exchange the code for tokens
        token_info = sp_oauth.get_access_token(code)
        
        if not token_info:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        # Test the token by getting user info
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_info = sp.current_user()
        
        # Redirect to frontend with success
        frontend_url = "http://localhost:3001"
        redirect_url = f"{frontend_url}?auth=success&user={urllib.parse.quote(user_info['display_name'] or user_info['id'])}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = "http://localhost:3001"
        redirect_url = f"{frontend_url}?auth=error&message={urllib.parse.quote(str(e))}"
        return RedirectResponse(url=redirect_url)

@app.get("/auth/status")
async def auth_status():
    """Check if user is authenticated"""
    try:
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if token_info:
            # Verify the token is still valid
            sp = spotipy.Spotify(auth=token_info['access_token'])
            user_info = sp.current_user()
            return {
                "authenticated": True,
                "user": {
                    "id": user_info['id'],
                    "display_name": user_info['display_name'],
                    "email": user_info.get('email'),
                    "followers": user_info['followers']['total'],
                    "images": user_info.get('images', [])
                }
            }
        else:
            return {"authenticated": False}
            
    except Exception as e:
        return {"authenticated": False, "error": str(e)}

@app.post("/auth/logout")
async def logout():
    """Logout user by clearing token cache"""
    try:
        # Remove the cached token file
        cache_path = ".spotify_cache"
        if os.path.exists(cache_path):
            os.remove(cache_path)
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error logging out: {str(e)}")

@app.get("/user/profile")
async def get_user_profile():
    """Get current user's Spotify profile"""
    try:
        sp_oauth = get_spotify_oauth()
        token_info = sp_oauth.get_cached_token()
        
        if not token_info:
            raise HTTPException(status_code=401, detail="Not authenticated")
        
        sp = spotipy.Spotify(auth=token_info['access_token'])
        user_info = sp.current_user()
        
        return {
            "id": user_info['id'],
            "display_name": user_info['display_name'],
            "email": user_info.get('email'),
            "followers": user_info['followers']['total'],
            "images": user_info.get('images', []),
            "country": user_info.get('country'),
            "product": user_info.get('product')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user profile: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
