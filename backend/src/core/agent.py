from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from .memory import memory
from .schema import ChatState
from .classifier import classify_query
from ..tools.spotify_tool import (
    get_top_tracks, 
    get_top_artists,
    get_playlist_names, 
    get_recently_played, 
    search_tracks, 
    get_saved_tracks,
    get_playlists_with_details,
    get_playlist_tracks,
    get_recent_playlists,
    search_artist_info,
    get_spotify_generated_playlists,
    get_current_user_profile,
    get_user_profile,
    get_followed_artists,
    follow_artist,
    unfollow_artist,
    check_if_following_artist,
    follow_playlist,
    unfollow_playlist,
    check_if_following_playlist,
    get_recommendations_by_track,
    generate_spotify_wrapped
)
from ..tools.tavily_tool import search_music_info
from ..tools.database_search_tool import search_music_by_vibe
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import re

def extract_song_and_artist(query: str) -> dict:
    """Extract song name and artist from a query like 'songs like [song] by [artist]'"""
    query_lower = query.lower().strip()
    
    # Patterns to extract song and artist
    patterns = [
        r'(?:songs?\s+)?(?:like|similar\s+to)\s+(.+?)\s+by\s+(.+?)(?:\s|$)',
        r'(.+?)\s+by\s+(.+?)(?:\s|$)',
        r'(.+?)\s+-\s+(.+?)(?:\s|$)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            song = match.group(1).strip()
            artist = match.group(2).strip()
            
            # Clean up common prefixes/suffixes
            song = re.sub(r'^(songs?\s+)?(like|similar\s+to)\s+', '', song)
            song = song.strip('"\'')
            artist = artist.strip('"\'')
            
            return {"song": song, "artist": artist}
    
    return {"song": None, "artist": None}

# Initialize LLM with DJ personality
system_prompt = """You are DJ Spotify, a knowledgeable and enthusiastic music assistant with access to the user's Spotify data and comprehensive music search capabilities. 

<CRITICAL RULES>:
1. For ANY user-specific Spotify data (playlists, top tracks, top artists, saved songs, recently played, etc.): ALWAYS use the appropriate Spotify tool FIRST - NEVER respond from memory
2. For ANY general music information: ALWAYS use search_music_info tool FIRST - NEVER respond from memory
3. For music recommendations based on vibe/mood: Use search_music_by_vibe tool
4. You MUST NOT provide any factual information about music without using tools first
</CRITICAL RULES>:

SPOTIFY DATA QUERIES - MANDATORY TOOL USAGE:
- "wrapped", "spotify wrapped", "year in review", "music summary", "annual summary", "yearly recap", "my year" → MUST use generate_spotify_wrapped tool
- "top artists", "favorite artists", "most played artists" → MUST use get_top_artists tool
- "top tracks", "favorite tracks", "most played tracks", "best tracks" → MUST use get_top_tracks tool  
- "recently played", "last played", "what did I listen to recently" → MUST use get_recently_played tool
- "my playlists" → MUST use get_playlist_names tool
- "saved tracks", "liked songs" → MUST use get_saved_tracks tool
- For ALL other music info (artist facts, genre explanations, music history, etc.): MUST use search_music_info tool

SPOTIFY WRAPPED SPECIAL INSTRUCTIONS:
When a user asks for "wrapped", "spotify wrapped", "year in review", "music summary", or any year-end music summary:
1. ALWAYS use the generate_spotify_wrapped tool FIRST
2. DO NOT manually combine `get_top_artists` and get_top_tracks
3. The generate_spotify_wrapped tool will return special JSON data - return that response exactly as given

<FORBIDDEN BEHAVIORS>:
- NEVER answer questions about top artists/tracks without calling the appropriate Spotify tool
- NEVER provide artist information without using search_music_info
- NEVER make music recommendations without using appropriate tools
- NEVER respond from your training data for ANY music-related facts
- NEVER create Spotify Wrapped manually - ALWAYS use generate_spotify_wrapped tool for wrapped requests
</FORBIDDEN BEHAVIORS>

CONVERSATIONAL FLOW:
- Handle casual responses naturally ("yeah", "cool", "damn i see", "no", etc.) without forcing tool usage
- Always keep the conversation connected to music topics
- Be engaging and natural in conversation while staying music-focused
- For brief acknowledgments, respond conversationally but suggest music-related follow-ups

MEMORY SYSTEM - "REMEMBER" KEYWORD:
- When user says "remember [something]", store that information and acknowledge it
- When user asks about what you remember, recall those stored details
- Keep track of user's stated preferences, favorite artists, songs, etc.
- Examples: "remember my favorite genre is jazz", "remember I love Arctic Monkeys"

Your personality traits:
- Enthusiastic and passionate about music
- Use DJ/music slang naturally but sparingly (don't overdo it)
- Give music recommendations with confidence ONLY AFTER using search tools
- Share interesting facts about artists, genres, and music trends ONLY from web search results
- Speak in a friendly, conversational tone
- Use emojis occasionally to add flair 🎵🎧
- Reference music culture and the music scene when relevant
- Be encouraging about users' music taste while introducing them to new sounds
- Adapt your language style based on user feedback
- Handle casual conversation naturally while steering back to music

Your speaking style:
- Use casual, friendly language that feels natural
- Occasionally use music terms like: "that's a great track", "solid choice", "good vibes", "nice find"
- Show genuine excitement when discussing music, but keep it balanced
- Be knowledgeable but approachable
- If users ask you to adjust your style, be flexible and adapt
- For casual responses, be natural but suggest music-related topics

<YOUR ROLE>
- Help users explore their Spotify data using Spotify tools
- Search for music information, artist details, and recommendations using web search
- Create a fun, engaging music discovery experience
- Always be helpful while maintaining your musical expertise
- Use tools for ALL factual information - never rely on training data
- Maintain natural conversation flow while keeping focus on music
- Remember user preferences when they use the "remember" keyword
</YOUR ROLE>

Remember: You're their knowledgeable music companion who gets information from reliable sources, not from memory! 🎤"""

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)  # Slightly higher temperature for more personality

# Register tools
tools = [
    get_top_tracks, get_top_artists, get_playlist_names, get_recently_played, search_tracks, get_saved_tracks,
    get_playlists_with_details, get_playlist_tracks, get_recent_playlists, search_artist_info, 
    get_spotify_generated_playlists, get_current_user_profile, get_user_profile, get_followed_artists,
    follow_artist, unfollow_artist, check_if_following_artist, follow_playlist, unfollow_playlist,
    check_if_following_playlist, search_music_info, search_music_by_vibe, get_recommendations_by_track,
    generate_spotify_wrapped
]
llm_with_tools = llm.bind_tools(tools)

# Classify query: returns "spotify", "web", or "database"
def router(state: ChatState) -> str:
    msg = state["messages"][-1].content
    classification = classify_query(msg)
    
    # Removed intent-based logging - now only logging based on actual tool execution
    return classification

# Handle tool invocation and LLM call

def call_model(state: ChatState) -> ChatState:
    messages = state["messages"]
    
    # Add system prompt to the beginning if not already present
    if not messages or not any(getattr(msg, 'content', '').startswith('You are DJ Spotify') for msg in messages):
        system_message = SystemMessage(content=system_prompt)
        messages = [system_message] + messages
    
    # Check if user is directly calling a tool name
    user_input = state["messages"][-1].content if state["messages"] else ""
    user_input_lower = user_input.lower().strip()
    
    # Define tool name mappings with helpful prompts that encourage natural conversation
    tool_prompts = {
        "get_recommendations_by_track": {
            "prompt": "Instead of using function names, just ask me naturally! Try something like:\n• 'Recommend songs like Bohemian Rhapsody by Queen'\n• 'Find music similar to that song by Taylor Swift'\n• 'I want songs like [song name] by [artist]'\n\nWhat song would you like recommendations based on? 🎵",
            "requires": ["track_name", "artist_name"]
        },
        "get_top_tracks": {
            "prompt": "Instead of function calls, just ask me naturally! Try:\n• 'Show me my top tracks'\n• 'What are my favorite songs?'\n• 'My most played music from this year'\n• 'Top tracks from last month'\n\nI'd love to show you your favorites! 🎶",
            "requires": []
        },
        "get_top_artists": {
            "prompt": "Let's keep it conversational! Instead of function names, try:\n• 'Who are my top artists?'\n• 'Show me my favorite musicians'\n• 'My most played artists this year'\n• 'Top artists from last month'\n\nI'd be happy to show you who you've been jamming to! 🎤",
            "requires": []
        },
        "search_music_by_vibe": {
            "prompt": "Let's talk music naturally! Instead of function calls, describe what you're feeling:\n• 'I want chill but danceable music'\n• 'Find me some sad acoustic songs'\n• 'Something energetic for working out'\n• 'Music similar to lo-fi but with vocals'\n\nWhat vibe are you going for? 🎧",
            "requires": ["query"]
        },
        "search_tracks": {
            "prompt": "Let's search naturally! Instead of function names, just tell me what you're looking for:\n• 'Find songs by Radiohead'\n• 'Search for that song from the 90s'\n• 'Look up Taylor Swift tracks'\n• 'I'm looking for [song/artist name]'\n\nWhat music are you trying to find? 🔍",
            "requires": ["query"]
        },
        "get_recently_played": {
            "prompt": "Just ask me naturally! Instead of function calls, try:\n• 'What did I listen to recently?'\n• 'Show me my recent music'\n• 'My last played songs'\n• 'What have I been playing lately?'\n\nI'd love to show you your recent listening history! 📅",
            "requires": []
        },
        "get_saved_tracks": {
            "prompt": "Let's keep it natural! Instead of function names, just ask:\n• 'Show me my saved songs'\n• 'What music have I liked?'\n• 'My favorite tracks'\n• 'Songs I've saved to my library'\n\nI'd be happy to show you your saved music! ❤️",
            "requires": []
        },
        "get_playlist_names": {
            "prompt": "Just ask me conversationally! Instead of function calls, try:\n• 'Show me my playlists'\n• 'What playlists do I have?'\n• 'List my music playlists'\n• 'My Spotify playlists'\n\nI'd love to show you all your playlists! 📂",
            "requires": []
        },
        "get_playlist_tracks": {
            "prompt": "Let's do this naturally! Instead of function names, tell me:\n• 'Show me songs from my Chill playlist'\n• 'What's in my Workout playlist?'\n• 'Tracks from [playlist name]'\n• 'Songs in my favorite playlist'\n\nWhich playlist would you like to explore? 📝",
            "requires": ["playlist_name"]
        },
        "search_artist_info": {
            "prompt": "Let's talk about artists naturally! Instead of function calls, just ask:\n• 'Tell me about Radiohead'\n• 'What do you know about Taylor Swift?'\n• 'Info on [artist name]'\n• 'Who is [artist]?'\n\nWhich artist are you curious about? 🎤",
            "requires": ["artist_name"]
        },
        "generate_spotify_wrapped": {
            "prompt": "Let's make this fun! Instead of function names, just say:\n• 'Create my Spotify Wrapped'\n• 'Show me my year in music'\n• 'My music summary'\n• 'What's my musical year been like?'\n\nI'd love to create your personalized music summary! 🎊",
            "requires": []
        },
        "search_music_info": {
            "prompt": "Just ask me naturally! Instead of function calls, tell me what you're curious about:\n• 'Tell me about jazz music'\n• 'Who invented the guitar?'\n• 'History of rock music'\n• 'What's the story behind [song/artist]?'\n\nWhat musical topic interests you? 🎼",
            "requires": ["query"]
        },
        "get_recommendations_by_audio_features": {
            "prompt": "Let's find music naturally! Instead of function names, describe what you want:\n• 'I want high energy, happy songs'\n• 'Find me danceable music'\n• 'Something with acoustic vibes'\n• 'Fast tempo electronic tracks'\n• 'Chill but upbeat music'\n\nWhat kind of musical characteristics are you in the mood for? 🎛️",
            "requires": []
        }
    }
    
    # Check if user input matches a tool name (direct function call)
    for tool_name, tool_info in tool_prompts.items():
        if user_input_lower == tool_name or user_input_lower == tool_name.replace('_', ' '):
            # Encourage natural conversation instead of direct function calls
            natural_prompt = f"I see you're looking for {tool_name.replace('_', ' ')}! Instead of using function names, just ask me naturally. {tool_info['prompt']}"
            response = AIMessage(content=natural_prompt)
            state["messages"].append(response)
            return {"messages": state["messages"]}
    
    # Check for "remember" keyword in user input
    user_input = state["messages"][-1].content if state["messages"] else ""
    if user_input.lower().startswith("remember "):
        # Extract what the user wants to remember
        memory_item = user_input[9:].strip()  # Remove "remember " prefix
        
        # Create a response acknowledging the memory and add it as a system note
        memory_note = f"[USER PREFERENCE: {memory_item}]"
        response_text = f"Got it! I'll remember that {memory_item}. 🎵 That's a solid preference to keep in mind for our music chats! Anything else you want to explore or discover? 🎧"
        
        # Add the memory as a system message for context, then the response
        system_memory = SystemMessage(content=memory_note)
        response = AIMessage(content=response_text)
        
        # Add both messages to maintain the memory context
        state["messages"].append(system_memory)
        state["messages"].append(response)
        return {"messages": state["messages"]}
    
    # Step 1: Model responds with a tool call (or regular message)
    response = llm_with_tools.invoke(messages)
    
    # Safety check: If response contains music facts without tool calls, force a tool call
    if isinstance(response, AIMessage) and not response.tool_calls:
        content = response.content.lower() if response.content else ""
        user_query = state["messages"][-1].content.lower().strip()
        
        # Don't force tool usage for conversational responses or short phrases
        conversational_phrases = [
            "yeah", "ok", "cool", "nice", "damn", "wow", "hmm", "sure", "alright", 
            "no", "yes", "bye", "hello", "hi", "thanks", "thank you", "lol",
            "i see", "got it", "makes sense", "interesting", "good", "bad", "awesome"
        ]
        
        # Check if it's just a conversational response (short and casual)
        is_conversational = (
            len(user_query.split()) <= 3 and 
            any(phrase in user_query for phrase in conversational_phrases)
        ) or user_query in ["👍", "👎", "🎵", "🎧", "😊", "😄", "😎"]
        
        # Only force tool usage if the response contains specific music facts AND it's not conversational
        music_fact_indicators = [
            "is a singer", "is a rapper", "is a band", "was born in", "formed in", 
            "their genre is", "they are known for", "their career began", "their discography",
            "albums include", "hit songs include", "originated in", "characterized by"
        ]
        
        # Check if user is asking a direct music question that needs factual answers
        direct_music_questions = [
            "who is", "what is", "when was", "where is", "how many", "tell me about",
            "what genre", "what style"
        ]
        
        # Check if user is asking for music recommendations (should use database search)
        recommendation_questions = [
            "recommend", "similar to", "like", "find me", "give me", "suggest", 
            "music for", "songs for", "tracks that", "chill", "danceable", "upbeat"
        ]
        
        needs_tool_usage = (
            not is_conversational and 
            (any(indicator in content for indicator in music_fact_indicators) or 
             any(question in user_query for question in direct_music_questions) or
             any(question in user_query for question in recommendation_questions))
        )
        
        if needs_tool_usage:
            # Determine which tool to use based on query classification
            query_type = classify_query(user_query)
            original_user_query = state["messages"][-1].content
            
            # Map classification to user-friendly names for logging
            classification_map = {
                "spotify": "Spotify API",
                "web": "Tavily Web Search", 
                "database": "Database Search"
            }
            
            print(f"[SAFETY] Forcing tool usage for query: {original_user_query}")
            print(f"[Classification] {classification_map.get(query_type, query_type)}")
            
            # Choose the appropriate tool based on classification
            if query_type == "database":
                tool_name = "search_music_by_vibe"
            elif query_type == "spotify":
                # Check if it's a wrapped request
                if any(keyword in original_user_query.lower() for keyword in ["wrapped", "year in review", "music summary", "yearly recap"]):
                    tool_name = "generate_spotify_wrapped"
                else:
                    # For other Spotify queries, default to a general search
                    tool_name = "search_music_info"
            else:  # web
                tool_name = "search_music_info"
            
            # Create a tool call
            if tool_name == "generate_spotify_wrapped":
                # For wrapped requests, determine time range from query
                time_range = "medium_term"  # default
                if "6 months" in original_user_query.lower() or "medium" in original_user_query.lower():
                    time_range = "medium_term"
                elif "4 weeks" in original_user_query.lower() or "month" in original_user_query.lower() or "short" in original_user_query.lower():
                    time_range = "short_term"
                elif "all time" in original_user_query.lower() or "long" in original_user_query.lower() or "year" in original_user_query.lower():
                    time_range = "long_term"
                
                tool_call = {
                    "name": tool_name,
                    "args": {"time_range": time_range},
                    "id": f"forced_search_{len(state['messages'])}"
                }
            else:
                tool_call = {
                    "name": tool_name,
                    "args": {"query": original_user_query},
                    "id": f"forced_search_{len(state['messages'])}"
                }
            
            response = AIMessage(
                content="Let me search for that information for you...",
                tool_calls=[tool_call]
            )
    
    # Only append the response to the original messages (without system prompt)
    state["messages"].append(response)

    # Step 2: If it's a tool call, handle it
    if isinstance(response, AIMessage) and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            # Map tool names to classification types for logging
            tool_classification_map = {
                "search_music_by_vibe": "Database Search",
                "search_music_info": "Tavily Web Search",
                "get_top_tracks": "Spotify API",
                "get_top_artists": "Spotify API", 
                "get_playlist_names": "Spotify API",
                "get_recently_played": "Spotify API",
                "search_tracks": "Spotify API",
                "get_saved_tracks": "Spotify API",
                "get_playlists_with_details": "Spotify API",
                "get_playlist_tracks": "Spotify API",
                "get_recent_playlists": "Spotify API",
                "search_artist_info": "Spotify API",
                "get_spotify_generated_playlists": "Spotify API",
                "get_current_user_profile": "Spotify API",
                "get_user_profile": "Spotify API",
                "get_followed_artists": "Spotify API",
                "follow_artist": "Spotify API",
                "unfollow_artist": "Spotify API",
                "check_if_following_artist": "Spotify API",
                "follow_playlist": "Spotify API",
                "unfollow_playlist": "Spotify API",
                "check_if_following_playlist": "Spotify API",
                "get_recommendations_by_track": "Spotify API",
                "generate_spotify_wrapped": "Spotify API"
            }
            
            classification = tool_classification_map.get(tool_name, "Unknown")
            print(f"[Tool Call] {tool_name}({tool_args}) → {classification}")

            try:
                # Find matching tool
                tool = next(t for t in tools if t.name == tool_name)
                tool_output = tool.invoke(tool_args or {})  # might be no args

                # Ensure tool output is never empty or None
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                # Special handling for Spotify Wrapped - preserve the original JSON data
                if tool_name == "generate_spotify_wrapped":
                    # For Spotify Wrapped, we want to return the tool output directly without LLM reprocessing
                    # Store the original response for final output
                    state["spotify_wrapped_response"] = str(tool_output)
                
                # Special handling for database search tool returning "specific_song_not_found"
                if tool_name == "search_music_by_vibe" and isinstance(tool_output, str):
                    try:
                        import json
                        parsed_output = json.loads(tool_output)
                        if (isinstance(parsed_output, dict) and 
                            parsed_output.get("error") == "specific_song_not_found"):
                            
                            print("[AUTO-FALLBACK] Database search found specific song not in DB, calling Spotify API...")
                            
                            # Extract song and artist from the original query
                            original_query = tool_args.get("query", "")
                            song_info = extract_song_and_artist(original_query)
                            
                            if song_info["song"] and song_info["artist"]:
                                # Import Spotify recommendation tool
                                from ..tools.spotify_tool import get_recommendations_by_track
                                
                                try:
                                    spotify_output = get_recommendations_by_track.invoke({
                                        "track_name": song_info["song"],
                                        "artist_name": song_info["artist"],
                                        "limit": tool_args.get("num_results", 10)
                                    })
                                    
                                    # Replace the "not found" message with actual Spotify recommendations
                                    tool_output = f"I found that song on Spotify! Here are some similar recommendations:\n\n{spotify_output}"
                                    print("[AUTO-FALLBACK] Successfully got Spotify recommendations")
                                    
                                except Exception as spotify_error:
                                    print(f"[AUTO-FALLBACK] Spotify fallback failed: {spotify_error}")
                                    tool_output = f"I couldn't find '{song_info['song']}' by '{song_info['artist']}' in the music database, and I'm having trouble accessing Spotify recommendations right now. You might want to check the song title or try a different approach."
                            else:
                                # Could not parse song/artist, use original error message
                                tool_output = parsed_output.get("message", "Song not found in database.")
                    except:
                        # If JSON parsing fails, use original tool output
                        pass
                
                # Step 3: Respond with tool output
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output),  # Ensure it's a string
                    )
                )
            except StopIteration:
                # Tool not found
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error: Tool '{tool_name}' not found.",
                    )
                )
            except Exception as e:
                # Tool execution error
                error_msg = f"Error executing tool '{tool_name}': {str(e)}"
                print(f"Tool error: {error_msg}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=error_msg,
                    )
                )

        # Step 4: Re-call model with tool response included (with system prompt)
        try:
            # Special handling for Spotify Wrapped - return original response directly
            if "spotify_wrapped_response" in state:
                wrapped_response = state["spotify_wrapped_response"]
                final_response = AIMessage(content=wrapped_response)
                state["messages"].append(final_response)
                return {"messages": state["messages"]}
            
            final_messages = [SystemMessage(content=system_prompt)] + state["messages"]
            final_response = llm_with_tools.invoke(final_messages)
            
            # Final safety check on the response
            if final_response.content:
                content_lower = final_response.content.lower()
                safety_phrases = [
                    "i don't have access to", "i can't access", "i would need to search",
                    "let me search for", "i should look that up", "i need to find that information"
                ]
                
                # If the model says it needs to search but didn't call tools, force another search
                if any(phrase in content_lower for phrase in safety_phrases) and not final_response.tool_calls:
                    print("[SAFETY] Model indicated need for search but didn't call tool")
                    final_response.content = "Let me search for that information for you! 🔍"
            
            # Ensure final response is never empty
            if not final_response.content or str(final_response.content).strip() == "":
                final_response.content = "Hmm, I'm having some trouble generating a response. Mind trying that again?"
            
            state["messages"].append(final_response)
        except Exception as e:
            # If final response fails, add error message with DJ personality
            error_msg = f"I hit a technical snag: {str(e)}. Let's try that again! 🎵"
            print(f"Final response error: {error_msg}")
            state["messages"].append(AIMessage(content=error_msg))

    else:
        # For regular messages (non-tool calls), ensure they're never empty
        if not response.content or str(response.content).strip() == "":
            response.content = "I'm not quite sure how to respond to that. Can you rephrase your question? 🎧"

    return {"messages": state["messages"]}

# LangGraph setup
builder = StateGraph(ChatState)

# Add nodes
builder.add_node("router", lambda x: x)  # just passes state through  
builder.add_node("spotify", call_model)
builder.add_node("web", call_model)
builder.add_node("database", call_model)

# Set entry point
builder.set_entry_point("router")

# Add conditional edges from router to specific handlers
builder.add_conditional_edges(
    "router", 
    router,
    {
        "spotify": "spotify",
        "web": "web",
        "database": "database"
    }
)

# Add edges to END
builder.add_edge("spotify", END)
builder.add_edge("web", END)
builder.add_edge("database", END)

# Compile graph with memory
graph = builder.compile(checkpointer=memory)
