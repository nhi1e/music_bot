from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
import json
from ..tools.database_search_tool import search_music_by_vibe

database_llm = ChatOpenAI(model="gpt-4o", temperature=0.7).bind_tools([search_music_by_vibe])
#TODO: create interface for agents so llm only needs to be bound once

def database_agent(state):
    """Database agent for music recommendations and vibe-based searches"""
    messages = state["messages"]
    
    print(f"[Database Agent] Processing query with {len(messages)} messages")
    
    # Call LLM with tools
    response = database_llm.invoke(messages)
    state["messages"].append(response)
    
    # Handle tool calls if present
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            print(f"[Database Agent] Executing tool: {tool_name}({tool_args})")
            
            try:
                # Execute the search_music_by_vibe tool
                tool_output = search_music_by_vibe.invoke(tool_args or {})
                
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                print(f"[Database Agent] Tool output: {len(str(tool_output))} characters")
                
                # Special handling for database search tool returning "specific_song_not_found"
                if isinstance(tool_output, str):
                    try:
                        parsed_output = json.loads(tool_output)
                        if (isinstance(parsed_output, dict) and 
                            parsed_output.get("error") == "specific_song_not_found"):
                            
                            # Extract song and artist information and suggest general search
                            song_info = parsed_output.get("extracted_info", {})
                            song = song_info.get("song", "Unknown")
                            artist = song_info.get("artist", "Unknown")
                            
                            tool_output = f"I couldn't find that specific song '{song}' by '{artist}' in our music database. Let me suggest some similar music based on the vibe you're looking for instead."
                    except:
                        pass  # If not JSON, proceed normally
                
                # Add tool response
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output)
                    )
                )
            except Exception as e:
                print(f"[Database Agent] Tool error: {e}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                )
        
        # Generate final response with tool results
        try:
            final_response = database_llm.invoke(state["messages"])
            state["messages"].append(final_response)
        except Exception as e:
            print(f"[Database Agent] Final response error: {e}")
            error_response = AIMessage(content="Sorry, I encountered an error processing your music recommendation request.")
            state["messages"].append(error_response)
    
    return {"messages": state["messages"]}
