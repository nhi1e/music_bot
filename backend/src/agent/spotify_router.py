def spotify_router(state):
    q = state["messages"][-1].content.lower()
    
    # Debug: Print state information
    print(f"[Spotify Router] Processing with {len(state['messages'])} messages")
    
    # Get conversation context to help with routing
    context_messages = []
    for msg in state["messages"][-10:]:  # Look at more messages for context
        if hasattr(msg, 'content') and msg.content:
            # Skip system messages when building context
            if not (hasattr(msg, 'content') and msg.content.startswith('You are DJ Spotify')):
                context_messages.append(msg.content.lower())
    
    context = " ".join(context_messages)
    
    # Check for Spotify Wrapped keywords (including "wrap")
    wrapped_keywords = ["wrapped", "wrap", "year in review", "music summary", "recap", "annual summary", "yearly recap", "my year", "spotify summary"]
    if any(k in q for k in wrapped_keywords):
        print(f"[Spotify Router] Routing to wrapped: keyword match")
        return "wrapped"
    
    # Check for contextual wrapped requests (continuation queries)
    continuation_patterns = ["how about", "how abt", "what about", "what abt", "and", "also", "too", "as well", "same for", "for", "now", "next"]
    if (len(q.split()) <= 4 and any(pattern in q for pattern in continuation_patterns) and
        any(wrapped_term in context for wrapped_term in wrapped_keywords)):
        print(f"[Spotify Router] Routing to wrapped: contextual continuation")
        return "wrapped"
    
    # Time period requests in wrapped context
    time_periods = ["month", "months", "week", "weeks", "year", "years", "days", "6 months", "1 month", "short_term", "medium_term", "long_term"]
    if (any(period in q for period in time_periods) and 
        any(wrapped_term in context for wrapped_term in wrapped_keywords)):
        print(f"[Spotify Router] Routing to wrapped: time period in wrapped context")
        return "wrapped"
    
    if any(k in q for k in ["playlist", "playlists"]):
        return "playlist"
    # Follow/unfollow actions should go to artist agent (includes contextual references)
    if any(k in q for k in ["follow", "unfollow", "start following", "stop following", "follow them", "unfollow them"]):
        return "artist"
    if any(k in q for k in ["artist", "artists", "band"]):
        return "artist"
    # Everything else about tracks, saved songs, recs, etc
    return "song"
