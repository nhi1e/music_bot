"""
Spotify tools for music recommendations
"""

from langchain_core.tools import tool
from .base import get_spotify_client

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
                    result += f"🎤 **More from {artist_name}:**\n"
        
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
