#!/usr/bin/env python3

"""
End-to-end test to verify the music bot behavior:
1. All music info queries should trigger tool calls
2. Tool calls should be logged
3. No built-in knowledge should be used
"""

import os
import sys
from src.agent.main_graph import graph
from app.schema import ChatState
from langchain_core.messages import HumanMessage

def test_query(query: str, test_name: str):
    """Test a single query and verify tool usage"""
    print(f"\n🧪 {test_name}")
    print("=" * 60)
    print(f"Query: {query}")
    print("-" * 60)
    
    # Initialize state
    state = ChatState(messages=[HumanMessage(content=query)])
    
    # Run the agent
    try:
        result = graph.invoke(state, config={"configurable": {"thread_id": "test"}})
        final_response = result["messages"][-1].content
        
        print(f"Response: {final_response}")
        print("✅ Query completed successfully")
        
        return final_response
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    print("🎵 Testing DJ Spotify Bot - End-to-End Verification")
    print("🚨 Look for [Tool Call] logs - every music question should trigger one!")
    
    # Test cases for music information (should use search_music_info)
    music_info_tests = [
        ("who is 2hollis", "Artist Information Query"),
        ("what is cloud rap", "Genre Information Query"), 
        ("tell me about jazz music", "Music History Query"),
        ("recommend some indie artists", "Recommendation Query"),
        ("what year was Nirvana formed", "Music Facts Query"),
    ]
    
    # Test cases for Spotify user data (should use Spotify tools)
    spotify_tests = [
        ("what are my top tracks", "User Top Tracks"),
        ("show me my playlists", "User Playlists"),
        ("what artists do I follow", "User Followed Artists"),
    ]
    
    print("\n📋 MUSIC INFORMATION TESTS (should use search_music_info)")
    for query, test_name in music_info_tests:
        test_query(query, test_name)
    
    print("\n📋 SPOTIFY USER DATA TESTS (should use Spotify tools)")
    for query, test_name in spotify_tests:
        test_query(query, test_name)
    
    print(f"\n🏁 Testing complete!")
    print("✅ Verify that [Tool Call] logs appeared for ALL queries above")
    print("❌ If any query lacks [Tool Call] logs, the bot used built-in knowledge!")

if __name__ == "__main__":
    main()
