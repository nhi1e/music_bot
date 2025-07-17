#!/usr/bin/env python3
"""
Test the new song similarity functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.classifier import classify_query
from app.tools.vector_search_tool import search_music_by_vibe
import json

def test_song_similarity_classifier():
    """Test that song similarity queries are properly classified"""
    
    print("Testing classifier for song similarity queries...")
    print("=" * 60)
    
    test_cases = [
        # Song similarity queries (should route to vector)
        ("Songs similar to Creep by Radiohead", "vector"),
        ("Music like Bohemian Rhapsody by Queen", "vector"),
        ("Find me tracks like Hotel California", "vector"),
        ("Similar to Yesterday by The Beatles", "vector"),
        ("Songs like Smells Like Teen Spirit", "vector"),
        ("Music similar to Wonderwall by Oasis", "vector"),
        
        # Regular vibe queries (should route to vector)
        ("Give me chill but danceable music", "vector"),
        ("Happy energetic songs", "vector"),
        
        # Information queries (should route to web)
        ("Who is Radiohead?", "web"),
        ("What genre is Creep?", "web"),
        ("Tell me about The Beatles", "web"),
        
        # Spotify queries (should route to spotify)
        ("What are my top songs?", "spotify"),
        ("Show me my playlists", "spotify")
    ]
    
    for query, expected in test_cases:
        result = classify_query(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{query}' -> {result} (expected: {expected})")

def test_song_similarity_search():
    """Test the actual song similarity search functionality"""
    
    print("\n\nTesting song similarity search...")
    print("=" * 60)
    
    test_queries = [
        "Songs similar to Creep by Radiohead",
        "Music like Bohemian Rhapsody by Queen", 
        "Tracks like Hotel California",
        "Similar to Yesterday by The Beatles",
        "Songs like Smells Like Teen Spirit by Nirvana"
    ]
    
    for query in test_queries:
        print(f"\nSearching: '{query}'")
        print("-" * 40)
        
        try:
            result = search_music_by_vibe.invoke({"query": query, "num_results": 5})
            parsed = json.loads(result)
            
            if "error" in parsed:
                print(f"Error: {parsed['error']}")
                continue
            
            recommendations = parsed.get("recommendations", [])
            
            if not recommendations:
                print("No recommendations found")
                continue
            
            print(f"Found {len(recommendations)} recommendations:")
            for i, rec in enumerate(recommendations[:3], 1):  # Show top 3
                print(f"  {i}. {rec['track']}")
                print(f"     Genre: {rec['genre']}")
                print(f"     Similarity: {rec['similarity_score']}")
                vibe = rec['vibe_profile']
                print(f"     Vibe: Energy={vibe['energy']}, Dance={vibe['danceability']}, Mood={vibe['mood']}")
                
        except Exception as e:
            print(f"Error testing '{query}': {e}")

def test_fallback_behavior():
    """Test fallback to regular vibe search when specific song not found"""
    
    print("\n\nTesting fallback behavior...")
    print("=" * 60)
    
    # Test with a song that probably doesn't exist in dataset
    test_query = "Songs similar to XYZ123 Nonexistent Song by Fake Artist"
    
    print(f"Testing fallback with: '{test_query}'")
    
    try:
        result = search_music_by_vibe.invoke({"query": test_query, "num_results": 3})
        parsed = json.loads(result)
        
        if "error" in parsed:
            print(f"Error: {parsed['error']}")
        else:
            recommendations = parsed.get("recommendations", [])
            if recommendations:
                print("✓ Fallback worked - got recommendations based on text analysis")
                print(f"  Found {len(recommendations)} recommendations")
            else:
                print("✗ No recommendations returned")
                
    except Exception as e:
        print(f"Error in fallback test: {e}")

if __name__ == "__main__":
    test_song_similarity_classifier()
    test_song_similarity_search()
    test_fallback_behavior()
