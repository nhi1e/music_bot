from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.spotify import (
    get_playlist_names, get_playlists_with_details, get_playlist_tracks,
    get_recent_playlists, follow_playlist, unfollow_playlist, check_if_following_playlist,
    create_playlist, add_track_to_playlist, remove_track_from_playlist, search_and_add_to_playlist
)

playlist_tools = [
    get_playlist_names, get_playlists_with_details, get_playlist_tracks,
    get_recent_playlists, follow_playlist, unfollow_playlist, check_if_following_playlist,
    create_playlist, add_track_to_playlist, remove_track_from_playlist, search_and_add_to_playlist
]
playlist_llm = ChatOpenAI(model="gpt-4o", temperature=0.7).bind_tools(playlist_tools)

def playlist_agent(state):
    """Spotify agent for playlist-related queries - playlist management and details"""
    messages = state["messages"]
    
    print(f"[Playlist Agent] Processing query with {len(messages)} messages")
    
    # Call LLM with tools
    response = playlist_llm.invoke(messages)
    state["messages"].append(response)
    
    # Handle tool calls if present
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            print(f"[Playlist Agent] Executing tool: {tool_name}({tool_args})")
            
            try:
                # Find matching tool
                tool = next(t for t in playlist_tools if t.name == tool_name)
                tool_output = tool.invoke(tool_args or {})
                
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                print(f"[Playlist Agent] Tool output: {len(str(tool_output))} characters")
                
                # Add tool response
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output)
                    )
                )
            except StopIteration:
                print(f"[Playlist Agent] Tool not found: {tool_name}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error: Tool '{tool_name}' not found."
                    )
                )
            except Exception as e:
                print(f"[Playlist Agent] Tool error: {e}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                )
        
        # Generate final response with tool results
        try:
            final_response = playlist_llm.invoke(state["messages"])
            state["messages"].append(final_response)
        except Exception as e:
            print(f"[Playlist Agent] Final response error: {e}")
            error_response = AIMessage(content="Sorry, I encountered an error processing your Spotify playlist request.")
            state["messages"].append(error_response)
    
    return {"messages": state["messages"]}
