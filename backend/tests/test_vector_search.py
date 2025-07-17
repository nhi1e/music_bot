#!/usr/bin/env python3
"""
Test script for vector search functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.classifier import classify_query
from app.tools.vector_search_tool import search_music_by_vibe
import json

def test_classifier():
    """Test the updated classifier"""
    print("Testing classifier...")
    
    test_queries = [
        ("Give me chill but danceable music", "vector"),
        ("Songs like the one I'm listening to", "vector"),
        ("Happy indie tracks with low energy and no vocals", "vector"),
        ("What is ambient music?", "web"),
        ("What are my top songs this month?", "spotify"),
        ("Music like lo-fi but with horns", "vector"),
        ("Who is Drake?", "web"),
        ("Show me my playlists", "spotify"),
        ("Find me upbeat electronic songs", "vector"),
        ("Tell me about jazz history", "web")
    ]
    
    for query, expected in test_queries:
        result = classify_query(query)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{query}' -> {result} (expected: {expected})")

def test_vector_search():
    """Test the vector search tool"""
    print("\nTesting vector search...")
    
    test_queries = [
        "Give me chill but danceable music",
        "Happy upbeat songs",
        "Sad acoustic tracks"
    ]
    
    for query in test_queries:
        print(f"\nSearching for: '{query}'")
        try:
            result = search_music_by_vibe.invoke({"query": query, "num_results": 5})
            # Parse the JSON result to make it more readable
            parsed = json.loads(result)
            print(f"Found {len(parsed.get('recommendations', []))} recommendations")
            if 'recommendations' in parsed:
                for i, rec in enumerate(parsed['recommendations'][:3], 1):  # Show first 3
                    print(f"  {i}. {rec['track']} (Genre: {rec['genre']}, Similarity: {rec['similarity_score']})")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_classifier()
    test_vector_search()
