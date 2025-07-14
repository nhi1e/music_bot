from langchain_core.tools import tool
import requests
import os

@tool
def search_music_info(query: str) -> str:
    """Use Tavily to search music-related info not available on Spotify."""
    api_key = os.getenv("TAVILY_API_KEY")
    resp = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"query": query}
    )
    return resp.json().get("answer", "No answer found.")
