from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from app.memory import memory
from app.schema import ChatState
from app.classifier import classify_query
from app.tools.spotify_tool import (
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
    check_if_following_playlist
)
from app.tools.tavily_tool import search_music_info
from langchain_openai import ChatOpenAI
from langchain_core.messages import ToolMessage, AIMessage
from langchain_core.tools import tool

# Initialize LLM with DJ personality
dj_system_prompt = """You are DJ Spotify, a cool and knowledgeable music chatbot with the personality of a professional DJ. 

Your personality traits:
- Enthusiastic and passionate about music
- Use DJ/music slang naturally but sparingly (don't overdo it)
- Give music recommendations with confidence 
- Share interesting facts about artists, genres, and music trends
- Speak in a friendly, conversational tone
- Use emojis occasionally to add flair 🎵🎧
- Reference music culture and the music scene when relevant
- Be encouraging about users' music taste while introducing them to new sounds
- Adapt your language style based on user feedback

Your speaking style:
- Use casual, friendly language that feels natural
- Occasionally use music terms like: "that's a great track", "solid choice", "good vibes", "nice find"
- Show genuine excitement when discussing music, but keep it balanced
- Be knowledgeable but approachable
- If users ask you to adjust your style, be flexible and adapt

Your role:
- Help users explore their Spotify data (top tracks, artists, playlists)
- Provide music recommendations and insights
- Search for information about artists and songs
- Create a fun, engaging music discovery experience
- Always be helpful while maintaining your musical expertise

Remember: You're their knowledgeable music companion who happens to have DJ expertise, not a caricature! 🎤"""

llm = ChatOpenAI(model="gpt-4o", temperature=0.7)  # Slightly higher temperature for more personality

# Register tools
tools = [
    get_top_tracks, get_top_artists, get_playlist_names, get_recently_played, search_tracks, get_saved_tracks,
    get_playlists_with_details, get_playlist_tracks, get_recent_playlists, search_artist_info, 
    get_spotify_generated_playlists, get_current_user_profile, get_user_profile, get_followed_artists,
    follow_artist, unfollow_artist, check_if_following_artist, follow_playlist, unfollow_playlist,
    check_if_following_playlist, search_music_info
]
llm_with_tools = llm.bind_tools(tools)

# Classify query: returns "spotify" or "web"
def router(state: ChatState) -> str:
    msg = state["messages"][-1].content
    return classify_query(msg)

# Handle tool invocation and LLM call

def call_model(state: ChatState) -> ChatState:
    messages = state["messages"]
    
    # Add system prompt to the beginning if not already present
    if not messages or not any(getattr(msg, 'content', '').startswith('You are DJ Spotify') for msg in messages):
        from langchain_core.messages import SystemMessage
        system_message = SystemMessage(content=dj_system_prompt)
        messages = [system_message] + messages
    
    # Step 1: Model responds with a tool call (or regular message)
    response = llm_with_tools.invoke(messages)
    
    # Only append the response to the original messages (without system prompt)
    state["messages"].append(response)

    # Step 2: If it's a tool call, handle it
    if isinstance(response, AIMessage) and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            print(f"[Tool Call] {tool_name}({tool_args})")

            try:
                # Find matching tool
                tool = next(t for t in tools if t.name == tool_name)
                tool_output = tool.invoke(tool_args or {})  # might be no args

                # Ensure tool output is never empty or None
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
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
            final_messages = [SystemMessage(content=dj_system_prompt)] + state["messages"]
            final_response = llm_with_tools.invoke(final_messages)
            
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

builder.set_entry_point("router")  
builder.add_conditional_edges("router", router)
builder.add_node("spotify", call_model)
builder.add_node("web", call_model)
builder.add_node("router", lambda x: x)  # just passes state through


# Compile graph with memory
graph = builder.compile(checkpointer=memory)
