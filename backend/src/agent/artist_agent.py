from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.spotify import (
    get_top_artists, search_artist_info, get_followed_artists,
    follow_artist, unfollow_artist, check_if_following_artist
)

artist_tools = [
    get_top_artists, search_artist_info, get_followed_artists,
    follow_artist, unfollow_artist, check_if_following_artist
]
artist_llm = ChatOpenAI(model="gpt-4o", temperature=0.7).bind_tools(artist_tools)

def artist_agent(state):
    """Spotify agent for artist-related queries - top artists, following, search"""
    messages = state["messages"]
    
    print(f"[Artist Agent] Processing query with {len(messages)} messages")
    
    # Call LLM with tools
    response = artist_llm.invoke(messages)
    state["messages"].append(response)
    
    # Handle tool calls if present
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            print(f"[Artist Agent] Executing tool: {tool_name}({tool_args})")
            
            try:
                # Find matching tool
                tool = next(t for t in artist_tools if t.name == tool_name)
                tool_output = tool.invoke(tool_args or {})
                
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                print(f"[Artist Agent] Tool output: {len(str(tool_output))} characters")
                
                # Add tool response
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output)
                    )
                )
            except StopIteration:
                print(f"[Artist Agent] Tool not found: {tool_name}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error: Tool '{tool_name}' not found."
                    )
                )
            except Exception as e:
                print(f"[Artist Agent] Tool error: {e}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                )
        
        # Generate final response with tool results
        try:
            final_response = artist_llm.invoke(state["messages"])
            state["messages"].append(final_response)
        except Exception as e:
            print(f"[Artist Agent] Final response error: {e}")
            error_response = AIMessage(content="Sorry, I encountered an error processing your Spotify artist request.")
            state["messages"].append(error_response)
    
    return {"messages": state["messages"]}
