from langchain_core.tools import tool
import requests
import os

@tool
def search_music_info(query: str) -> str:
    """Use Tavily to search for music-related information including artist details, genre info, music history, and recommendations. Always use this tool for any music facts, artist information, or recommendations rather than relying on built-in knowledge."""
    
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Tavily API key not configured. Please set TAVILY_API_KEY environment variable to enable music information search. For now, I can help you with your Spotify data instead!"
    
    # Enhance music-related queries with context
    music_enhanced_query = query
    if any(word in query.lower() for word in ["who is", "whos", "tell me about"]):
        # Add music context to artist queries
        if not any(music_word in query.lower() for music_word in ["artist", "musician", "singer", "rapper", "band", "music"]):
            music_enhanced_query = f"{query} artist musician music"
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "query": music_enhanced_query,
                "search_depth": "advanced",
                "include_answer": True,
                "max_results": 8,  # Increased for better music results
                "include_domains": ["spotify.com", "genius.com", "allmusic.com", "musicbrainz.org", "last.fm", "bandcamp.com", "soundcloud.com"]  # Music-focused domains
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", "")
            results = data.get("results", [])
            
            if answer:
                return f"🎵 {answer}"
            elif results:
                # If no direct answer, compile info from search results
                info_pieces = []
                for result in results[:3]:  # Use top 3 results
                    if result.get("content"):
                        info_pieces.append(result["content"][:200] + "...")
                
                if info_pieces:
                    return f"Based on my search: " + " ".join(info_pieces)
            
            return f"I searched for '{query}' but couldn't find detailed information. The search completed but returned limited results."
        
        elif response.status_code == 401:
            return "Tavily API authentication failed. Please check the API key configuration."
        else:
            return f"Search service returned error {response.status_code}. Unable to fetch music information at the moment."
            
    except requests.exceptions.Timeout:
        return "Search request timed out. Please try again with a simpler query."
    except requests.exceptions.RequestException as e:
        return f"Network error while searching: {str(e)}"
    except Exception as e:
        return f"Unexpected error during search: {str(e)}"
