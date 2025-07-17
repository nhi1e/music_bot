import re

def classify_query(query: str) -> str:
    """
    Classify queries to determine if they need Spotify tools, web search, or vector search.
    
    Returns:
    - "spotify": For user-specific Spotify data queries
    - "web": For general music information, artist facts, etc.
    - "vector": For music recommendation based on characteristics/vibe
    """
    q = query.lower()
    
    # Spotify-specific user data queries
    spotify_keywords = [
        "my", "top tracks", "top artists", "my playlist", "my music", 
        "recently played", "saved tracks", "liked songs", "following",
        "spotify profile", "user profile", "follow artist", "unfollow",
        "current user", "playlist tracks"
    ]
    
    # Vector search keywords for music recommendation based on vibe/characteristics
    vector_keywords = [
        "chill", "danceable", "upbeat", "energetic", "mellow", "relaxing",
        "happy", "sad", "melancholic", "aggressive", "peaceful", "intense",
        "high energy", "low energy", "acoustic", "electronic", "instrumental",
        "with vocals", "no vocals", "fast tempo", "slow tempo", "dreamy",
        "atmospheric", "ambient", "lo-fi", "similar to", "like", "vibe",
        "mood", "feels like", "reminds me of", "music for", "songs for",
        "tracks that", "find music", "recommend", "suggestion", "songs"
    ]
    
    # Patterns that strongly indicate song similarity requests
    similarity_patterns = [
        r"similar to .+",
        r"like .+ by .+",
        r"songs like .+",
        r"music like .+", 
        r"tracks like .+",
        r"sounds like .+",
        r"reminds me of .+",
        r".+ by .+ but .+",
        r"find .+ similar to .+"
    ]
    
    # General music information queries (should use Tavily)
    web_keywords = [
        "what is", "who is", "tell me about", "genre", "style", "history",
        "facts about", "information about", "explain", "describe", 
        "biography", "discography", "albums", "songs by", "music theory",
        "instruments", "band members", "career", "influences", "awards"
    ]
    
    # Check for explicit Spotify user data queries
    if any(keyword in q for keyword in spotify_keywords):
        return "spotify"
    
    # Check for song similarity patterns first (highest priority for vector search)
    if any(re.search(pattern, q) for pattern in similarity_patterns):
        return "vector"
    
    # Check for vector search queries (music recommendations based on vibe/characteristics)
    if any(keyword in q for keyword in vector_keywords):
        return "vector"
        
    # Additional patterns that suggest vector search
    vector_patterns = [
        "music like", "songs like", "tracks like", "similar to",
        "give me", "find me", "recommend", "suggestion", 
        "vibe", "mood", "feel", "energy", "tempo"
    ]
    if any(pattern in q for pattern in vector_patterns):
        return "vector"
    
    # Check for general music information queries
    if any(keyword in q for keyword in web_keywords):
        return "web"
    
    # If query mentions specific artists, genres, or music terms without "my", route to web
    if any(word in q for word in ["artist", "album", "music", "genre", "band"]) and "my" not in q:
        # But check if it's asking for recommendations first
        if any(word in q for word in ["like", "similar", "recommend", "suggest", "find", "give me"]):
            return "vector"
        return "web"
    
    # Check if it's a general songs request (likely wanting recommendations)
    if "songs" in q and any(word in q for word in ["happy", "sad", "energetic", "chill", "upbeat", "mellow", "fast", "slow"]):
        return "vector"
    
    # Default to web search for safety (avoid using built-in knowledge)
    return "web"
