def classify_query(query: str) -> str:
    """
    Classify queries to determine if they need Spotify tools or web search.
    
    Returns:
    - "spotify": For user-specific Spotify data queries
    - "web": For general music information, artist facts, recommendations, etc.
    """
    q = query.lower()
    
    # Spotify-specific user data queries
    spotify_keywords = [
        "my", "top tracks", "top artists", "my playlist", "my music", 
        "recently played", "saved tracks", "liked songs", "following",
        "spotify profile", "user profile", "follow artist", "unfollow",
        "current user", "playlist tracks"
    ]
    
    # General music information queries (should use Tavily)
    web_keywords = [
        "what is", "who is", "tell me about", "genre", "style", "history",
        "recommend", "similar to", "like", "facts about", "information about",
        "explain", "describe", "cloud rap", "hip hop", "rock", "pop", "jazz",
        "electronic", "country", "folk", "classical", "indie", "alternative",
        "biography", "discography", "albums", "songs by", "music theory",
        "instruments", "band members", "career", "influences", "awards"
    ]
    
    # Check for explicit Spotify user data queries
    if any(keyword in q for keyword in spotify_keywords):
        return "spotify"
    
    # Check for general music information queries
    if any(keyword in q for keyword in web_keywords):
        return "web"
    
    # If query mentions specific artists, genres, or music terms without "my", route to web
    if any(word in q for word in ["artist", "song", "album", "music", "genre", "band"]) and "my" not in q:
        return "web"
    
    # Default to web search for safety (avoid using built-in knowledge)
    return "web"
