def classify_query(query: str) -> str:
    q = query.lower()
    if any(w in q for w in ["playlist", "top", "spotify", "artist", "audiobook"]):
        return "spotify"
    return "web"
