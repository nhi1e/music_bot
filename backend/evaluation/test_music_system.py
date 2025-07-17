#!/usr/bin/env python3
"""
Simple test of music recommendation system before RAGAs evaluation
"""

import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import json
from app.tools.vector_search_tool import search_music_by_vibe

def test_music_system():
    """Test the music recommendation system"""
    
    print("🎵 Testing Music Recommendation System")
    print("=" * 50)
    
    test_queries = [
        "Give me upbeat electronic dance music",
        "Find chill acoustic songs for relaxation", 
        "I want energetic rock music for working out"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 30)
        
        try:
            result = search_music_by_vibe.invoke({
                "query": query,
                "num_results": 3
            })
            
            parsed = json.loads(result)
            
            if "error" in parsed:
                print(f"❌ Error: {parsed['error']}")
            elif "recommendations" in parsed:
                print(f"✅ Found {len(parsed['recommendations'])} recommendations:")
                for j, rec in enumerate(parsed['recommendations'], 1):
                    print(f"   {j}. {rec['track']}")
                    print(f"      Similarity: {rec['similarity_score']:.3f}")
                    if 'vibe_profile' in rec:
                        vibe = rec['vibe_profile']
                        print(f"      Vibe: Energy={vibe.get('energy', 'N/A')}, "
                              f"Danceability={vibe.get('danceability', 'N/A')}")
            else:
                print("❌ No recommendations found")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print(f"\n{'='*50}")
    print("✅ Music system test completed!")

if __name__ == "__main__":
    test_music_system()
