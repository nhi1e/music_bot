#!/usr/bin/env python3
"""
Test script to verify the bot NEVER uses built-in knowledge
"""

import asyncio
from app.agent import graph
from langchain_core.messages import HumanMessage

async def test_tool_usage():
    """Test that the bot uses tools for ALL music information"""
    
    test_cases = [
        # General music knowledge (should ALWAYS use search_music_info)
        "What is cloud rap?",
        "Who is Tyler the Creator?", 
        "Tell me about jazz music",
        "What genre is Radiohead?",
        "Who are artists similar to Billie Eilish?",
        "Explain the history of hip hop",
        "What instruments are used in rock music?",
        "Who founded Def Jam Records?",
        "What is the difference between house and techno?",
        "Recommend some indie folk artists",
        
        # User-specific Spotify data (should use Spotify tools)
        "What are my top tracks?",
        "Show me my playlists",
        "What artists do I follow?",
        "Play my recently played songs",
        
        # Edge cases that might trick the LLM into using built-in knowledge
        "Is Kanye West a rapper?",  # Should search, not use built-in knowledge
        "What year was Nirvana formed?",  # Should search, not use built-in knowledge
        "How many Grammy awards does Beyoncé have?",  # Should search, not use built-in knowledge
    ]
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {question}")
        print('='*60)
        
        state = {"messages": [HumanMessage(content=question)]}
        config = {"configurable": {"thread_id": f"test_session_{i}"}}
        
        try:
            result = await graph.ainvoke(state, config=config)
            response = result["messages"][-1].content
            print(f"Response: {response}")
            
            # Check if tools were called by looking for tool call logs
            print(f"✅ Tool usage verification: Look for [Tool Call] logs above")
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Give some time between requests
        await asyncio.sleep(2)

    print(f"\n{'='*60}")
    print("🧪 TESTING COMPLETE")
    print("✅ Verify that [Tool Call] logs appear for ALL questions")
    print("❌ If any response lacks [Tool Call] logs, the bot used built-in knowledge!")
    print('='*60)

if __name__ == "__main__":
    print("🧪 Testing tool usage behavior...")
    print("🚨 CRITICAL: Every question should trigger a [Tool Call] log!")
    asyncio.run(test_tool_usage())
