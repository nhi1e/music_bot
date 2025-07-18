import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import Word2Vec
from langchain_core.tools import tool
import os
import re
from typing import List, Dict, Any
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables for Spotify
load_dotenv()

class MusicVectorSearcher:
    def __init__(self, csv_path: str = None):
        self.csv_path = csv_path or os.path.join(os.path.dirname(__file__), '../../data/dataset.csv')
        self.song_data = None
        self.word2vec_model = None
        self.embedded_song_df = None
        self.embedding_dim = 15 
        self.load_and_preprocess_data()
    
    
    def load_and_preprocess_data(self):
        """Load and preprocess the music dataset following the vector.py approach"""
        try:
            # Load original dataset
            raw_song_df = pd.read_csv(self.csv_path)
            print(f"Loaded dataset with {len(raw_song_df)} rows")
            
            # Remove rows with corrupted data (extremely long strings in numeric columns)
            # Check for reasonable song names and artists (less than 200 chars)
            raw_song_df = raw_song_df[
                (raw_song_df['track_name'].str.len() < 200) & 
                (raw_song_df['artists'].str.len() < 200)
            ]
            print(f"After filtering corrupted rows: {len(raw_song_df)} rows")
            
            # 1. Pre process - Add "song_" prefix to all columns
            song_df = raw_song_df.add_prefix("song_")
            song_df = song_df.drop(columns=["song_Unnamed: 0"], errors='ignore')
            
            # Rename track columns to song columns for consistency
            song_df = song_df.rename(columns={
                'song_track_name': 'song_name',
                'song_track_id': 'song_id',
                'song_track_genre': 'song_genre'
            })
            
            # Handle missing values in critical columns
            song_df["song_name"] = song_df["song_name"].fillna("Unknown Song")
            song_df["song_artists"] = song_df["song_artists"].fillna("Unknown Artist")
            
            # Fix artist column - remove quotes and brackets
            def fix_artist(str_list):
                # Handle NaN values and convert to string
                if pd.isna(str_list):
                    return "Unknown Artist"
                str_list = str(str_list)
                return ", ".join([v for v in str_list.rstrip("']").lstrip("['").split("', '")])
            
            song_df["song_artists"] = song_df["song_artists"].apply(fix_artist)
            
            # Create song description by combining name and artists
            song_df.insert(0, "song_description", song_df["song_name"] + " - " + song_df["song_artists"])
            
            # Remove duplicates based on song description
            self.song_data = song_df[~song_df.duplicated(subset=["song_description"], keep="first")].reset_index(drop=True)
            
            print(f"Preprocessed dataset with {len(self.song_data)} unique rows")
            
            # 2. Create song vector embeddings
            self.create_embeddings()
            
        except Exception as e:
            print(f"Error loading and preprocessing dataset: {e}")
            self.song_data = None
    
    def tokenize_text(self, text):
        """Simple tokenization function"""
        # Handle NaN values
        if pd.isna(text):
            return []
        # Convert to lowercase and split by spaces, removing punctuation
        cleaned_text = re.sub(r'[^\w\s]', ' ', str(text).lower())
        return [word for word in cleaned_text.split() if word.strip()]
    
    def create_embeddings(self):
        """Create combined embeddings following the vector.py approach"""
        if self.song_data is None or len(self.song_data) == 0:
            return
        
        # Tokenize the descriptions
        tokenized_song_descs = [
            self.tokenize_text(v.lower()) for v in self.song_data["song_description"]
        ]
        
        # Train Word2Vec model
        self.word2vec_model = Word2Vec(
            sentences=tokenized_song_descs,
            vector_size=self.embedding_dim,
            window=5,
            min_count=1,
            sg=1,
        )
        
        print(f"Trained Word2Vec model with vocabulary size: {len(self.word2vec_model.wv.key_to_index)}")
        
        # Create categorical embeddings using the get_embedding function
        def get_embedding(song_desc_tokens, model, embedding_dim):
            vectors = [model.wv[token] for token in song_desc_tokens if token in model.wv]
            return sum(vectors) / len(vectors) if vectors else np.zeros(embedding_dim)
        
        categorical_embeddings = [
            get_embedding(song_desc_tokens, self.word2vec_model, self.embedding_dim) 
            for song_desc_tokens in tokenized_song_descs
        ]
        
        # Get numeric columns (excluding name, artists, description, and metadata columns)
        exclude_cols = ["song_name", "song_artists", "song_description", "song_album_name", "song_genre", "song_explicit", "song_id"]
        numeric_cols = [col for col in self.song_data.columns if col not in exclude_cols and self.song_data[col].dtype in ['int64', 'float64']]
        
        print(f"Using numeric columns: {numeric_cols}")
        
        # Fill NaN values in numeric columns with column means before scaling
        for col in numeric_cols:
            self.song_data[col] = pd.to_numeric(self.song_data[col], errors='coerce')  # Convert to numeric, set invalid to NaN
            self.song_data[col] = self.song_data[col].fillna(self.song_data[col].mean())
        
        # Scale numeric columns
        scaled_numeric_cols = [
            (self.song_data[col] - self.song_data[col].mean()) / np.std(self.song_data[col])
            for col in numeric_cols
        ]
        numeric_embeddings = list(map(list, zip(*scaled_numeric_cols)))
        
        # Merge the embeddings
        row_embeddings = [
            np.concatenate([cat_row, num_row])
            for cat_row, num_row in zip(categorical_embeddings, numeric_embeddings)
        ]
        
        # Create dataframe with embeddings
        self.embedded_song_df = self.song_data[["song_name", "song_artists"]].copy()
        self.embedded_song_df["song_embedding"] = row_embeddings
        
        print(f"Created embeddings with shape: {np.array(row_embeddings).shape}")
    
    def find_similar_to_song(self, song_name: str, artist_name: str = None) -> np.ndarray:
        """Find a specific song in the dataset and return its embedding"""
        if self.embedded_song_df is None:
            return None
        
        # Create search patterns
        song_lower = song_name.lower().strip()
        artist_lower = artist_name.lower().strip() if artist_name else None
        
        # Try to find exact matches
        song_titles = self.embedded_song_df['song_name'].str.lower()
        song_artists = self.embedded_song_df['song_artists'].str.lower()
        
        matches = []
        
        # Find exact song title matches
        song_mask = song_titles.str.contains(song_lower, na=False, regex=False)
        if artist_lower:
            artist_mask = song_artists.str.contains(artist_lower, na=False, regex=False)
            exact_matches = song_mask & artist_mask
            if exact_matches.any():
                idx = exact_matches.idxmax()  # Get first match
                return self.embedded_song_df.iloc[idx]['song_embedding'].reshape(1, -1)
        
        # If no exact match with artist, try song title only
        if song_mask.any():
            idx = song_mask.idxmax()
            return self.embedded_song_df.iloc[idx]['song_embedding'].reshape(1, -1)
        
        return None

    def text_to_vector(self, query: str) -> np.ndarray:
        """Convert query text to vector representation using the trained Word2Vec model"""
        # First, check if this is a "similar to [song]" type query
        similar_patterns = [
            r'similar to (.+)',
            r'like (.+)',
            r'songs like (.+)',
            r'music like (.+)',
            r'tracks like (.+)'
        ]
        
        for pattern in similar_patterns:
            match = re.search(pattern, query.lower())
            if match:
                song_reference = match.group(1).strip()
                
                # Try to parse "song by artist" format
                by_match = re.search(r'(.+?)\s+by\s+(.+)', song_reference)
                if by_match:
                    song_name = by_match.group(1).strip()
                    artist_name = by_match.group(2).strip()
                    
                    # Try to find this specific song in our dataset
                    song_vector = self.find_similar_to_song(song_name, artist_name)
                    if song_vector is not None:
                        print(f"Found similar song match for: '{song_name}' by '{artist_name}'")
                        return song_vector
                else:
                    # Just song name, try to find it
                    song_vector = self.find_similar_to_song(song_reference)
                    if song_vector is not None:
                        print(f"Found similar song match for: '{song_reference}'")
                        return song_vector
        
        # If no specific song found, create vector from query text
        tokenized_query = self.tokenize_text(query.lower())
        
        # Get embeddings for words in vocabulary
        def get_embedding(tokens, model, embedding_dim):
            vectors = [model.wv[token] for token in tokens if token in model.wv]
            return sum(vectors) / len(vectors) if vectors else np.zeros(embedding_dim)
        
        # Create text embedding
        query_text_embedding = get_embedding(tokenized_query, self.word2vec_model, self.embedding_dim)
        
        # Create dummy numeric features (neutral values)
        # Get the number of numeric features from the dataset
        if self.song_data is not None:
            numeric_cols = [col for col in self.song_data.columns 
                          if col not in ["song_name", "song_artists", "song_description", "song_album_name", "song_genre", "song_explicit", "song_id"] 
                          and self.song_data[col].dtype in ['int64', 'float64']]
            # Use neutral values (0.5 for most features, scaled to mean=0)
            neutral_numeric = np.zeros(len(numeric_cols))  # Already scaled, so 0 is neutral
            
            # Combine text and numeric embeddings
            combined_query_vector = np.concatenate([query_text_embedding, neutral_numeric])
            return combined_query_vector.reshape(1, -1)
        
        # Fallback if no dataset loaded
        return query_text_embedding.reshape(1, -1)

    def _search_spotify_for_similar(self, song_reference: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search Spotify for songs similar to the given reference"""
        try:
            # Get Spotify client
            scope = "user-top-read playlist-read-private user-read-recently-played user-library-read"
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
                scope=scope,
                cache_path=".spotify_cache"
            ))
            
            # Search for tracks on Spotify
            results = sp.search(q=song_reference, type='track', limit=num_results)
            
            if not results['tracks']['items']:
                return []
            
            spotify_results = []
            for track in results['tracks']['items']:
                artist_names = ', '.join([artist['name'] for artist in track['artists']])
                
                # Get audio features if available
                try:
                    audio_features = sp.audio_features([track['id']])[0]
                    if audio_features:
                        audio_data = {
                            'danceability': float(audio_features.get('danceability', 0)),
                            'energy': float(audio_features.get('energy', 0)),
                            'valence': float(audio_features.get('valence', 0)),
                            'acousticness': float(audio_features.get('acousticness', 0)),
                            'instrumentalness': float(audio_features.get('instrumentalness', 0)),
                            'tempo': float(audio_features.get('tempo', 0))
                        }
                    else:
                        audio_data = {
                            'danceability': 0.5, 'energy': 0.5, 'valence': 0.5,
                            'acousticness': 0.5, 'instrumentalness': 0.5, 'tempo': 120
                        }
                except:
                    audio_data = {
                        'danceability': 0.5, 'energy': 0.5, 'valence': 0.5,
                        'acousticness': 0.5, 'instrumentalness': 0.5, 'tempo': 120
                    }
                
                result = {
                    'track_name': track['name'],
                    'artists': artist_names,
                    'similarity': 1.0,  # High similarity since it's from search
                    'audio_features': audio_data,
                    'popularity': track.get('popularity', 0),
                    'source': 'spotify_search'
                }
                
                spotify_results.append(result)
            
            return spotify_results
            
        except Exception as e:
            print(f"Error searching Spotify: {e}")
            return []

    def _extract_song_reference_for_search(self, query: str) -> str:
        """Extract song reference from query for text-based search when song not found in DB"""
        query_lower = query.lower()
        
        # Patterns that indicate specific song requests
        similarity_patterns = [
            r'similar to (.+)',
            r'like (.+)',
            r'songs like (.+)',
            r'music like (.+)',
            r'tracks like (.+)',
            r'sounds like (.+)',
            r'reminds me of (.+)'
        ]
        
        for pattern in similarity_patterns:
            match = re.search(pattern, query_lower)
            if match:
                song_reference = match.group(1).strip()
                
                # Try to parse "song by artist" format
                by_match = re.search(r'(.+?)\s+by\s+(.+)', song_reference)
                if by_match:
                    song_name = by_match.group(1).strip()
                    artist_name = by_match.group(2).strip()
                    
                    # Check if this song exists in our dataset
                    song_exists = self._song_exists_in_db(song_name, artist_name)
                    if not song_exists:
                        # Return the song and artist names for text-based search
                        return f"{song_name} {artist_name}"
                else:
                    # Just song name, check if it exists
                    song_exists = self._song_exists_in_db(song_reference)
                    if not song_exists:
                        # Return the song reference for text-based search
                        return song_reference
        
        return None
    
    def _song_exists_in_db(self, song_name: str, artist_name: str = None) -> bool:
        """Check if a song exists in the database"""
        if self.song_data is None:
            return False
        
        song_lower = song_name.lower().strip()
        song_titles = self.song_data['song_name'].str.lower()
        
        # Check for song title matches
        song_mask = song_titles.str.contains(song_lower, na=False, regex=False)
        
        if artist_name:
            artist_lower = artist_name.lower().strip()
            song_artists = self.song_data['song_artists'].str.lower()
            artist_mask = song_artists.str.contains(artist_lower, na=False, regex=False)
            exact_matches = song_mask & artist_mask
            return exact_matches.any()
        else:
            return song_mask.any()

    def _extract_genre_filter(self, query: str) -> str:
        """Extract genre from query if specified"""
        query_lower = query.lower()
        
        # Common genre keywords
        genre_patterns = {
            'k-pop': ['k-pop', 'kpop', 'korean pop'],
            'pop': ['pop music', 'pop songs'],
            'rock': ['rock music', 'rock songs'],
            'jazz': ['jazz music', 'jazz songs'],
            'hip-hop': ['hip-hop', 'hip hop', 'rap'],
            'country': ['country music', 'country songs'],
            'classical': ['classical music', 'classical songs'],
            'electronic': ['electronic music', 'edm'],
            'r-n-b': ['r&b', 'rnb', 'r-n-b'],
            'reggae': ['reggae music', 'reggae songs'],
            'folk': ['folk music', 'folk songs'],
            'indie': ['indie music', 'indie songs'],
            'metal': ['metal music', 'metal songs'],
            'blues': ['blues music', 'blues songs']
        }
        
        for genre, patterns in genre_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return genre
        
        return None
    
    def _is_popularity_query(self, query: str) -> bool:
        """Check if query is asking for popular songs"""
        popularity_keywords = ['popular', 'top', 'hit', 'chart', 'trending', 'famous', 'best']
        return any(keyword in query.lower() for keyword in popularity_keywords)
    
    def _get_popular_songs_by_genre(self, genre: str, top_k: int) -> List[Dict[str, Any]]:
        """Get popular songs from a specific genre"""
        genre_mask = self.song_data['song_genre'].str.lower() == genre.lower()
        genre_songs = self.song_data[genre_mask].copy()
        
        if genre_songs.empty:
            return []
        
        # Sort by popularity and get top songs
        popular_songs = genre_songs.nlargest(top_k, 'song_popularity')
        
        results = []
        for idx, song in popular_songs.iterrows():
            results.append({
                'track_name': song['song_name'],
                'artists': song['song_artists'], 
                'similarity': 1.0,  # Max similarity for exact genre match
                'audio_features': {
                    'danceability': float(song.get('song_danceability', 0)),
                    'energy': float(song.get('song_energy', 0)),
                    'valence': float(song.get('song_valence', 0)),
                    'acousticness': float(song.get('song_acousticness', 0)),
                    'instrumentalness': float(song.get('song_instrumentalness', 0)),
                    'tempo': float(song.get('song_tempo', 0))
                },
                'popularity': int(song.get('song_popularity', 0))
            })
        
        return results

    def search_similar_music(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search for music similar to the text description using combined embeddings"""
        if self.embedded_song_df is None:
            return []

        # Check if this is a "similar to [specific song]" query that's not in our DB
        song_reference = self._extract_song_reference_for_search(query)
        if song_reference:
            print(f"Song not found in database, searching Spotify: '{song_reference}'")
            # Use Spotify search to find similar songs
            spotify_results = self._search_spotify_for_similar(song_reference, top_k)
            if spotify_results:
                return spotify_results
            else:
                print("No Spotify results found, falling back to text search")
                # Fall back to text search if Spotify doesn't return results
                search_query = song_reference
        else:
            search_query = query

        # Check for genre-specific queries
        genre_filter = self._extract_genre_filter(search_query)
        
        # Create working dataset (filtered by genre if specified)
        if genre_filter:
            genre_mask = self.song_data['song_genre'].str.lower() == genre_filter.lower()
            if genre_mask.any():
                print(f"Filtering for {genre_filter} songs: {genre_mask.sum()} found")
                filtered_indices = genre_mask[genre_mask].index
                working_df = self.embedded_song_df.loc[filtered_indices].copy()
                working_song_data = self.song_data.loc[filtered_indices].copy()
            else:
                print(f"No {genre_filter} songs found, searching all genres")
                working_df = self.embedded_song_df.copy()
                working_song_data = self.song_data.copy()
        else:
            working_df = self.embedded_song_df.copy()
            working_song_data = self.song_data.copy()

        # Check for popularity-based queries
        if self._is_popularity_query(search_query) and genre_filter:
            # For popularity queries with genre filter, sort by popularity instead of similarity
            return self._get_popular_songs_by_genre(genre_filter, top_k)

        # Convert query to vector representation
        query_vector = self.text_to_vector(search_query)
        
        # Check if query vector is valid
        if query_vector is None or query_vector.size == 0:
            print("Warning: Could not create valid query vector")
            return []

        # Get song embeddings as a matrix from working dataset
        song_embeddings = np.vstack(working_df['song_embedding'].values)
        
        # Calculate similarities using cosine similarity
        try:
            similarities = cosine_similarity(query_vector, song_embeddings)[0]
        except Exception as e:
            print(f"Error calculating similarities: {e}")
            return []

        # Get top matches
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            track = working_df.iloc[idx]
            # Get original song data for additional features  
            original_idx = working_df.index[idx]
            original_track = working_song_data.loc[original_idx]
            
            result = {
                'track_name': track['song_name'],
                'artists': track['song_artists'], 
                'similarity': float(similarities[idx]),
                'audio_features': {
                    'danceability': float(original_track.get('song_danceability', 0)),
                    'energy': float(original_track.get('song_energy', 0)),
                    'valence': float(original_track.get('song_valence', 0)),
                    'acousticness': float(original_track.get('song_acousticness', 0)),
                    'instrumentalness': float(original_track.get('song_instrumentalness', 0)),
                    'tempo': float(original_track.get('song_tempo', 0))
                },
                'source': 'local_database'
            }
            
            # Add popularity if available
            if 'song_popularity' in original_track:
                result['popularity'] = int(original_track['song_popularity'])
                
            results.append(result)

        return results

# Initialize the searcher globally
_searcher = None

def get_searcher():
    global _searcher
    if _searcher is None:
        _searcher = MusicVectorSearcher()
    return _searcher

@tool
def search_music_by_vibe(query: str, num_results: int = 10) -> str:
    """
    Search for music based on descriptive characteristics, mood, vibe, or similarity to specific songs.
    
    This tool finds music that matches descriptive queries like:
    - "Chill but danceable music"
    - "Happy indie tracks with low energy"
    - "Music like lo-fi but with horns"
    - "Energetic electronic songs"
    - "Sad acoustic songs"
    - "Songs similar to Creep by Radiohead"
    - "Music like Bohemian Rhapsody by Queen"
    - "Tracks like Hotel California"
    
    Args:
        query: Descriptive text about the desired music characteristics or reference to a specific song
        num_results: Number of recommendations to return (default: 10)
    
    Returns:
        JSON string with music recommendations
    """
    try:
        searcher = get_searcher()
        results = searcher.search_similar_music(query, top_k=num_results)
        
        if not results:
            return json.dumps({
                "error": "No music recommendations found. The dataset might not be loaded properly."
            })
        
        # Format results for better readability
        formatted_results = {
            "query": query,
            "recommendations": []
        }
        
        for i, track in enumerate(results, 1):
            track_info = {
                "rank": i,
                "track": f"{track['track_name']} by {track['artists']}",
                "similarity_score": round(track['similarity'], 3),
                "source": track.get('source', 'local_database'),
                "vibe_profile": {
                    "danceability": round(track['audio_features']['danceability'], 2),
                    "energy": round(track['audio_features']['energy'], 2),
                    "mood": "positive" if track['audio_features']['valence'] > 0.5 else "mellow",
                    "style": "acoustic" if track['audio_features']['acousticness'] > 0.5 else "electronic",
                    "vocals": "minimal" if track['audio_features']['instrumentalness'] > 0.5 else "prominent"
                }
            }
            
            # Add popularity if available
            if 'popularity' in track:
                track_info["popularity"] = track['popularity']
                
            formatted_results["recommendations"].append(track_info)
        
        return json.dumps(formatted_results, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Error searching for music: {str(e)}"
        })
