import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

spotify = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
))

def spotify_recommendation(preferences: str) -> str:
    genre = preferences.lower().strip()
    try:
        results = spotify.recommendations(seed_genres=[genre], limit=1)
        if results and results["tracks"]:
            track = results["tracks"][0]
            return f"{track['name']} by {track['artists'][0]['name']}"
    except Exception:
        pass
    return "Sorry, I couldn't find a good recommendation for that genre."

def mood_to_genre_or_feature(mood: str) -> dict:
    mood_map = {
        "happy": {"seed_genres": ["pop", "dance"], "target_valence": 0.9},
        "sad": {"seed_genres": ["acoustic", "piano"], "target_valence": 0.2},
        "chill": {"seed_genres": ["chill", "ambient"], "target_energy": 0.2},
        "excited": {"seed_genres": ["edm", "party"], "target_energy": 0.9},
        "angry": {"seed_genres": ["metal", "rock"], "target_energy": 0.95},
        "tired": {"seed_genres": ["sleep", "ambient"], "target_energy": 0.1},
        "moody": {"seed_genres": ["r-n-b", "alternative"], "target_valence": 0.3},
        "calm": {"seed_genres": ["classical", "jazz"], "target_energy": 0.15},
        "hype": {"seed_genres": ["hip-hop", "trap"], "target_energy": 0.95}
    }

    for key in mood_map:
        if key in mood.lower():
            return mood_map[key]
    return {"seed_genres": ["pop"]}
