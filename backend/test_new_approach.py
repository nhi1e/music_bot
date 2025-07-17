#!/usr/bin/env python3
"""
Test the new preprocessing and embedding approach
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.tools.vector_search_tool import search_music_by_vibe
import json

def test_preprocessing():
    """Test the preprocessing steps"""
    print("Testing new preprocessing and embedding approach...")
    
    test_queries = [
        "Give me chill but danceable music",
        "Happy upbeat electronic songs", 
        "Sad acoustic tracks with vocals",
        "Lo-fi instrumental music",
        "Fast energetic rock songs"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: '{query}'")
        
        try:
            result = search_music_by_vibe.invoke({"query": query, "num_results": 5})
            parsed = json.loads(result)
            
            if 'error' in parsed:
                print(f"❌ Error: {parsed['error']}")
            elif 'recommendations' in parsed:
                print(f"✅ Found {len(parsed['recommendations'])} recommendations")
                for i, rec in enumerate(parsed['recommendations'][:3], 1):
                    print(f"  {i}. {rec['track']}")
                    print(f"     Genre: {rec['genre']}, Similarity: {rec['similarity_score']}")
                    if 'vibe_profile' in rec:
                        vibe = rec['vibe_profile']
                        print(f"     Vibe: {vibe['mood']}, {vibe['style']}, {vibe['vocals']} vocals")
            else:
                print("❌ Unexpected response format")
                
        except Exception as e:
            print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_preprocessing()
