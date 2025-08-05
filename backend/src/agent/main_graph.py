from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
import json
import re
from .spotify_router import spotify_router
from .playlist_agent import playlist_agent
from .artist_agent import artist_agent
from .song_agent import song_agent
from .wrapped_agent import wrapped_agent
from .web_agent import web_agent
from .database_agent import database_agent
from ..core.schema import ChatState
from ..core.memory import memory

# DJ Spotify system prompt for the multiagent system
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
- "top tracks", "top songs", "favorite tracks", "most played tracks", "best tracks" → MUST use get_top_tracks tool
- "top genre", "most played genre", "favorite genre", "main genre" (standalone genre requests) → MUST use get_top_artists tool
- "recently played", "last played", "what did I listen to recently" → MUST use get_recently_played tool
- "my playlists" → MUST use get_playlist_names tool
- "saved tracks", "liked songs" → MUST use get_saved_tracks tool
- "follow them", "unfollow them" → Extract artist name from conversation context and use follow_artist/unfollow_artist tools
- For ALL other music info (artist facts, genre explanations, music history, etc.): MUST use search_music_info tool

CONTEXTUAL UNDERSTANDING:
- When user says "them", "him", "her", "it" referring to artists, look back in conversation to identify the specific artist
- When user asks "who is [artist]" then later says "follow them", "them" refers to that artist
- Extract artist names from conversation history to resolve pronouns and contextual references
- Always use the most recently mentioned artist when resolving contextual references

IMPORTANT DISTINCTIONS:
- "top songs" = get_top_tracks (NOT recently played, NOT wrapped)
- "most played genre recently" = get_top_artists (NOT wrapped)
- "spotify wrapped" = generate_spotify_wrapped (comprehensive summary with UI)

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

# Initialize main LLM
llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

def handle_memory_and_conversation(state: ChatState) -> ChatState:
    """Handle memory system and conversational elements before routing to agents"""
    messages = state["messages"]
    
    # Add system prompt to the beginning if not already present
    if not messages or not any(getattr(msg, 'content', '').startswith('You are DJ Spotify') for msg in messages):
        system_message = SystemMessage(content=system_prompt)
        messages = [system_message] + messages
        state["messages"] = messages
    
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
    
    # Check for conversational responses that don't need tool usage
    user_input_lower = user_input.lower().strip()
    conversational_phrases = [
        "yeah", "ok", "cool", "nice", "damn", "wow", "hmm", "sure", "alright", 
        "no", "yes", "bye", "hello", "hi", "thanks", "thank you", "lol",
        "i see", "got it", "makes sense", "interesting", "good", "bad", "awesome"
    ]
    
    # Before treating as conversational, check if it's a contextual action response
    # Look for recent context that might make "yes/no" meaningful for Spotify actions
    recent_context = []
    for msg in messages[-6:]:  # Look at last 6 messages for context
        if hasattr(msg, 'content') and msg.content:
            recent_context.append(msg.content.lower())
    
    context_text = " ".join(recent_context)
    
    # Check if "yes" or "no" is in response to a follow/unfollow question
    if user_input_lower in ["yes", "yeah", "sure", "yep", "y"]:
        if any(follow_indicator in context_text for follow_indicator in [
            "follow", "would you like to follow", "want to follow", "follow them", 
            "follow on spotify", "start following"]):
            # This "yes" is likely confirming a follow action - don't treat as conversational
            return state
    
    if user_input_lower in ["no", "nah", "nope", "n"]:
        if any(follow_indicator in context_text for follow_indicator in [
            "follow", "would you like to follow", "want to follow", "follow them",
            "follow on spotify", "start following", "unfollow", "stop following"]):
            # This "no" is likely declining a follow action - don't treat as conversational
            return state
    
    is_conversational = (
        len(user_input_lower.split()) <= 3 and 
        any(phrase in user_input_lower for phrase in conversational_phrases)
    ) or user_input_lower in ["👍", "👎", "🎵", "🎧", "😊", "😄", "😎"]
    
    # Additional check: if there's recent follow/artist context, don't treat short responses as conversational
    if (user_input_lower in ["yes", "no", "yeah", "nah", "sure", "yep", "nope"] and
        any(follow_context in context_text for follow_context in [
            "follow", "artist", "blackpink", "spotify", "would you like"])):
        is_conversational = False
    
    if is_conversational:
        # Handle conversational responses naturally
        conversational_responses = {
            "yeah": "Right on! 🎵 What's next on your musical journey?",
            "cool": "Awesome! 🎧 Want to discover something new?",
            "nice": "Glad you like it! What else can I help you explore?",
            "thanks": "You're welcome! Always here for your music needs 🎶",
            "ok": "Sweet! What other musical adventures should we dive into?",
            "good": "Nice! 🎵 Ready for more music exploration?",
            "awesome": "Right?! 🎧 Let's keep the music flowing - what's next?"
        }
        
        response_text = conversational_responses.get(user_input_lower, 
            "Right on! 🎵 What else can I help you discover in the world of music?")
        
        response = AIMessage(content=response_text)
        state["messages"].append(response)
        return {"messages": state["messages"]}
    
    return state

def classify_with_context(messages: list) -> str:
    """Classifier that considers conversation context"""
    current_query = messages[-1].content.lower() if messages else ""
    
    # Get recent conversation context (last 3-4 messages for context)
    context_messages = []
    for msg in messages[-6:]:  # Look at last 6 messages (3 user + 3 assistant pairs)
        if hasattr(msg, 'content') and msg.content:
            context_messages.append(msg.content.lower())
    
    context = " ".join(context_messages)
    
    print(f"[Classifier] Current query: {current_query}")
    print(f"[Classifier] Context: {context[:200]}...")
    
    # Direct Spotify Wrapped detection (including "wrap" keyword)
    wrapped_keywords = ["wrapped", "wrap", "year in review", "music summary", "recap", "annual summary", "yearly recap", "my year"]
    if any(keyword in current_query for keyword in wrapped_keywords):
        print(f"[Classifier] Direct Spotify Wrapped detection")
        return "spotify"
    
    # Time periods + context suggesting wrapped (e.g., "6 months" after wrapped discussion)
    time_periods = ["month", "months", "week", "weeks", "year", "years", "days", "6 months", "1 month", "4 weeks"]
    if (any(period in current_query for period in time_periods) and 
        any(wrapped_term in context for wrapped_term in wrapped_keywords)):
        print(f"[Classifier] Time period in wrapped context")
        return "spotify"
    
    # Check for conversational continuations
    continuation_patterns = [
        "how about", "how abt", "what about", "what abt", "and", "also",
        "too", "as well", "same for", "for", "now", "next"
    ]
    
    # Check for contextual references that need Spotify actions
    contextual_spotify_patterns = [
        r"follow (them|him|her|it)",           # "follow them"
        r"unfollow (them|him|her|it)",         # "unfollow them" 
        r"add (them|him|her|it|this|that)",    # "add them to playlist"
        r"save (them|him|her|it|this|that)",   # "save this song"
        r"like (them|him|her|it|this|that)",   # "like this artist"
        r"follow .+ on spotify",               # "follow them on spotify"
        r"add .+ to playlist",                 # "add this to playlist"
    ]
    
    # Check if current query has contextual references that suggest Spotify actions
    if any(re.search(pattern, current_query) for pattern in contextual_spotify_patterns):
        # Look for artist/song mentions in recent context to confirm it's a Spotify action
        # Also check for recent artist names that could be resolved from "them/him/her"
        context_indicators = [
            "artist", "song", "track", "music", "album", "spotify", "playlist",
            "top", "recently", "listening", "played"
        ]
        
        # Look for potential artist names in recent context
        artist_name_patterns = [
            r"who is ([a-zA-Z0-9\s]+)",
            r"whos ([a-zA-Z0-9\s]+)", 
            r"tell me about ([a-zA-Z0-9\s]+)",
            r"([a-zA-Z0-9\s]+) is a",
            r"([a-zA-Z0-9\s]+) artist",
            r"([a-zA-Z0-9\s]+) musician"
        ]
        
        recent_artist = None
        for msg_content in context_messages[-3:]:  # Check last 3 messages for artist names
            for pattern in artist_name_patterns:
                match = re.search(pattern, msg_content, re.IGNORECASE)
                if match:
                    recent_artist = match.group(1).strip()
                    break
            if recent_artist:
                break
        
        if any(indicator in context for indicator in context_indicators) or recent_artist:
            print(f"[Classifier] Contextual Spotify action detected: {current_query}")
            if recent_artist:
                print(f"[Classifier] Recent artist context: {recent_artist}")
            return "spotify"
    
    # Special handling for "yes/no" responses that might be confirming Spotify actions
    if current_query.strip() in ["yes", "yeah", "sure", "yep", "y", "no", "nah", "nope", "n"]:
        # Check if there's recent follow-related context
        if any(follow_indicator in context for follow_indicator in [
            "follow", "would you like to follow", "want to follow", "follow them",
            "follow on spotify", "start following", "blackpink", "artist"]):
            print(f"[Classifier] Contextual follow response detected: {current_query}")
            return "spotify"
        
        # Check if there's recent playlist-related context
        if any(playlist_indicator in context for playlist_indicator in [
            "playlist", "add to playlist", "create playlist", "would you like to add"]):
            print(f"[Classifier] Contextual playlist response detected: {current_query}")
            return "spotify"
    
    # If current query is short and seems like a continuation
    if (len(current_query.split()) <= 3 and 
        any(pattern in current_query for pattern in continuation_patterns)):
        
        # Check what was discussed recently in context
        if any(spotify_term in context for spotify_term in [
            "top tracks", "top artists", "my playlist", "recently played", 
            "saved tracks", "spotify", "wrapped", "my music"]):
            
            # Check for Spotify Wrapped context specifically
            if any(wrapped_term in context for wrapped_term in [
                "wrapped", "wrap", "year in review", "music summary", "annual summary", "yearly recap", "my year"]):
                print(f"[Classifier] Contextual routing: spotify (wrapped from context)")
                return "spotify"
            # Determine what specific Spotify topic based on current query + context
            elif "artist" in current_query or ("top" in context and "track" in context and "artist" in current_query):
                print(f"[Classifier] Contextual routing: spotify (artists from context)")
                return "spotify"
            elif "track" in current_query or "song" in current_query:
                print(f"[Classifier] Contextual routing: spotify (tracks from context)")
                return "spotify"
            elif "playlist" in current_query:
                print(f"[Classifier] Contextual routing: spotify (playlists from context)")
                return "spotify"
            else:
                # General Spotify context detected
                print(f"[Classifier] Contextual routing: spotify (general from context)")
                return "spotify"
    
    # For ambiguous queries about artists/tracks, check context
    if current_query in ["artists", "tracks", "songs", "playlists"]:
        if any(spotify_term in context for spotify_term in [
            "top", "my", "recently", "saved", "spotify", "wrapped"]):
            print(f"[Classifier] Contextual routing: spotify ('{current_query}' in Spotify context)")
            return "spotify"
    
    # Expand common abbreviations and informal language
    query_expansions = {
        "how abt": "how about",
        "what abt": "what about", 
        "artists": "top artists",
        "tracks": "top tracks",
        "songs": "top songs",
        "follow them": "follow artist",
        "unfollow them": "unfollow artist",
        "add them": "add to playlist",
        "save them": "save tracks"
    }
    
    expanded_query = current_query
    for abbrev, expansion in query_expansions.items():
        if abbrev in expanded_query:
            expanded_query = expanded_query.replace(abbrev, expansion)
    
    # If query was expanded and now contains Spotify keywords, use Spotify
    if expanded_query != current_query:
        # Check expanded query against Spotify keywords
        spotify_keywords = ["wrapped", "wrap", "spotify wrapped", "year in review", "music summary", 
                           "top tracks", "top artists", "my playlist", "my music", "recently played"]
        if any(keyword in expanded_query for keyword in spotify_keywords):
            print(f"[Classifier] Expanded '{current_query}' to '{expanded_query}' -> spotify")
            return "spotify"
    
    # Final classification using base classifier logic integrated here
    # Database search keywords for music recommendation based on vibe/characteristics
    database_keywords = [
        "chill", "danceable", "upbeat", "energetic", "mellow", "relaxing",
        "happy", "sad", "melancholic", "aggressive", "peaceful", "intense",
        "high energy", "low energy", "acoustic", "electronic", "instrumental",
        "with vocals", "no vocals", "fast tempo", "slow tempo", "dreamy",
        "atmospheric", "ambient", "lo-fi", "vibe", "mood", "feels like", 
        "reminds me of", "music for", "songs for", "tracks that"
    ]
    
    # Recommendation patterns
    recommendation_patterns = [
        r"recommend (me )?some", r"suggest (me )?some", r"find me (some )?music",
        r"give me (some )?songs", r"i want (some )?music", r"music for .+",
        r"songs for .+", r"what should i listen to", r"looking for .+ music",
        r"need .+ songs", r"similar to .+", r"like .+ by .+", r"songs like .+"
    ]
    
    # Check for recommendation requests
    if any(keyword in current_query for keyword in database_keywords):
        if any(rec_word in current_query for rec_word in ["recommend", "suggest", "find", "give me", "i want", "looking for", "need"]):
            print(f"[Classifier] Database recommendation request detected")
            return "database"
    
    if any(re.search(pattern, current_query) for pattern in recommendation_patterns):
        print(f"[Classifier] Database similarity/recommendation pattern detected")
        return "database"
    
    # Default to web for general music information
    print(f"[Classifier] Defaulting to web search")
    return "web"

def router(state: ChatState) -> str:
    """Enhanced router with memory and conversation handling"""
    # First handle memory and conversational elements
    updated_state = handle_memory_and_conversation(state)
    
    # If we handled a memory or conversational response, we're done
    if len(updated_state["messages"]) > len(state["messages"]):
        # Update the state with the new messages
        state["messages"] = updated_state["messages"]
        return "conversation_handled"
    
    # Otherwise, proceed with context-aware routing
    classification = classify_with_context(state["messages"])
    
    print(f"[Main Router] Query: {state['messages'][-1].content}")
    print(f"[Main Router] Classification: {classification}")
    print(f"[Main Router] Total messages being passed: {len(state['messages'])}")
    
    return classification
# 1. Build the Spotify subgraph
spotify_builder = StateGraph(ChatState)
spotify_builder.add_node("spotify_router", lambda x: x)
spotify_builder.add_node("playlist", playlist_agent)
spotify_builder.add_node("artist", artist_agent)
spotify_builder.add_node("song", song_agent)
spotify_builder.add_node("wrapped", wrapped_agent)
spotify_builder.set_entry_point("spotify_router")
spotify_builder.add_conditional_edges(
    "spotify_router", spotify_router,
    {"playlist": "playlist", "artist": "artist", "song": "song", "wrapped": "wrapped"}
)
for node in ["playlist", "artist", "song", "wrapped"]:
    spotify_builder.add_edge(node, END)
spotify_subgraph = spotify_builder.compile()  

# 2. Create a conversation handler node for memory/conversational responses
def conversation_handler(state: ChatState) -> ChatState:
    """Handle when we've already processed memory or conversational responses"""
    return {"messages": state["messages"]}

# 3. Build the main graph
main_builder = StateGraph(ChatState)
main_builder.add_node("router", lambda x: x)
main_builder.add_node("spotify", spotify_subgraph)
main_builder.add_node("web", web_agent)
main_builder.add_node("database", database_agent)
main_builder.add_node("conversation_handler", conversation_handler)

main_builder.set_entry_point("router")

main_builder.add_conditional_edges(
    "router", router,
    {
        "spotify": "spotify", 
        "web": "web", 
        "database": "database",
        "conversation_handled": "conversation_handler"
    }
)

for node in ["spotify", "web", "database", "conversation_handler"]:
    main_builder.add_edge(node, END)

graph = main_builder.compile(checkpointer=memory)
