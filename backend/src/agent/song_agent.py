from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.spotify import (
    get_top_tracks, get_recently_played, search_tracks, get_saved_tracks,
    get_recommendations_by_track
)

song_tools = [
    get_top_tracks, get_recently_played, search_tracks, get_saved_tracks,
    get_recommendations_by_track
]
song_llm = ChatOpenAI(model="gpt-4o", temperature=0.7).bind_tools(song_tools)

def song_agent(state):
    """Spotify agent for song-related queries - tracks, saved songs, recommendations"""
    messages = state["messages"]
    
    print(f"[Song Agent] Processing query with {len(messages)} messages")
    
    # Call LLM with tools
    response = song_llm.invoke(messages)
    state["messages"].append(response)
    
    # Handle tool calls if present
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            print(f"[Song Agent] Executing tool: {tool_name}({tool_args})")
            
            try:
                # Find matching tool
                tool = next(t for t in song_tools if t.name == tool_name)
                tool_output = tool.invoke(tool_args or {})
                
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                print(f"[Song Agent] Tool output: {len(str(tool_output))} characters")
                
                # Add tool response
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output)
                    )
                )
            except StopIteration:
                print(f"[Song Agent] Tool not found: {tool_name}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error: Tool '{tool_name}' not found."
                    )
                )
            except Exception as e:
                print(f"[Song Agent] Tool error: {e}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                )
        
        # Generate final response with tool results
        try:
            final_response = song_llm.invoke(state["messages"])
            state["messages"].append(final_response)
        except Exception as e:
            print(f"[Song Agent] Final response error: {e}")
            error_response = AIMessage(content="Sorry, I encountered an error processing your Spotify song request.")
            state["messages"].append(error_response)
    
    return {"messages": state["messages"]}
