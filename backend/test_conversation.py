#!/usr/bin/env python3

"""
Test the improved conversational flow and remember functionality
"""

import asyncio
from app.agent import graph
from langchain_core.messages import HumanMessage

async def test_conversation_flow():
    """Test that casual responses don't trigger tool usage"""
    
    print("🎵 Testing Improved Conversational Flow")
    print("=" * 60)
    
    state = {"messages": []}
    config = {"configurable": {"thread_id": "conversation_test"}}
    
    # Test cases that should NOT trigger tool calls
    casual_responses = [
        "yeah",
        "cool", 
        "damn i see",
        "no",
        "awesome",
        "lol",
        "nice"
    ]
    
    print("\n🗣️ TESTING CASUAL RESPONSES (should NOT trigger tools)")
    print("-" * 50)
    
    for response in casual_responses:
        print(f"\n💬 User: {response}")
        
        state["messages"].append(HumanMessage(content=response))
        state = await graph.ainvoke(state, config=config)
        bot_response = state["messages"][-1].content
        
        print(f"🤖 DJ Spotify: {bot_response}")
        print(f"📊 Messages: {len(state['messages'])}")

async def test_remember_functionality():
    """Test the remember keyword functionality"""
    
    print("\n\n🧠 TESTING REMEMBER FUNCTIONALITY")
    print("=" * 60)
    
    state = {"messages": []}
    config = {"configurable": {"thread_id": "remember_test"}}
    
    # Test remember functionality
    remember_tests = [
        "remember my favorite genre is indie rock",
        "remember I love Arctic Monkeys", 
        "remember my name is Alex",
        "what do you remember about me?"
    ]
    
    for test_input in remember_tests:
        print(f"\n💬 User: {test_input}")
        
        state["messages"].append(HumanMessage(content=test_input))
        state = await graph.ainvoke(state, config=config)
        bot_response = state["messages"][-1].content
        
        print(f"🤖 DJ Spotify: {bot_response}")
        print(f"📊 Messages: {len(state['messages'])}")

async def test_music_questions():
    """Test that actual music questions still trigger tools"""
    
    print("\n\n🎸 TESTING MUSIC QUESTIONS (should trigger tools)")
    print("=" * 60)
    
    state = {"messages": []}
    config = {"configurable": {"thread_id": "music_questions_test"}}
    
    music_questions = [
        "who is Taylor Swift?",
        "what genre is rock music?", 
        "recommend some jazz artists"
    ]
    
    for question in music_questions:
        print(f"\n💬 User: {question}")
        
        state["messages"].append(HumanMessage(content=question))
        state = await graph.ainvoke(state, config=config)
        bot_response = state["messages"][-1].content
        
        print(f"🤖 DJ Spotify: {bot_response[:100]}...")
        print(f"📊 Messages: {len(state['messages'])}")

if __name__ == "__main__":
    asyncio.run(test_conversation_flow())
    asyncio.run(test_remember_functionality()) 
    asyncio.run(test_music_questions())
