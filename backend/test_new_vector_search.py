#!/usr/bin/env python3
"""
Test script for the updated vector_search_tool.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from app.tools.vector_search_tool import search_music_by_vibe
import json

def test_vector_search():
    """Test the new vector search functionality"""
    
    print("🎵 Testing Music Vector Search Tool")
    print("=" * 50)
    
    # Test cases
    test_queries = [
        "chill electronic music",
        "upbeat danceable songs", 
        "sad acoustic ballads",
        "songs similar to Bohemian Rhapsody",
        "energetic rock music"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query}'")
        print("-" * 30)
        
        try:
            result = search_music_by_vibe.invoke({"query": query, "num_results": 3})
            result_data = json.loads(result)
            
            if "error" in result_data:
                print(f"❌ Error: {result_data['error']}")
            else:
                print(f"✅ Found {len(result_data['recommendations'])} recommendations:")
                for rec in result_data['recommendations']:
                    print(f"   {rec['rank']}. {rec['track']} (similarity: {rec['similarity_score']})")
                    print(f"      Vibe: {rec['vibe_profile']}")
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_vector_search()
