from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.spotify import generate_spotify_wrapped

wrapped_llm = ChatOpenAI(model="gpt-4o", temperature=0.7).bind_tools([generate_spotify_wrapped])

def wrapped_agent(state):
    """Spotify agent for generating Spotify Wrapped - year in review summaries"""
    messages = state["messages"]
    
    print(f"[Wrapped Agent] Processing Spotify Wrapped request with {len(messages)} messages")
    
    # Call LLM with tools
    response = wrapped_llm.invoke(messages)
    state["messages"].append(response)
    
    # Handle tool calls if present
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            print(f"[Wrapped Agent] Executing tool: {tool_name}({tool_args})")
            
            try:
                # Execute the generate_spotify_wrapped tool
                tool_output = generate_spotify_wrapped.invoke(tool_args or {})
                
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                print(f"[Wrapped Agent] Tool output: {len(str(tool_output))} characters")
                
                # Special handling for Spotify Wrapped - preserve the original JSON data
                if tool_name == "generate_spotify_wrapped":
                    # Store the original response for potential frontend processing
                    state["spotify_wrapped_response"] = str(tool_output)
                
                # Add tool response
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output)
                    )
                )
            except Exception as e:
                print(f"[Wrapped Agent] Tool error: {e}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                )
        
        # Generate final response with tool results
        try:
            # Special handling for Spotify Wrapped - return original response directly if available
            if "spotify_wrapped_response" in state:
                wrapped_response = AIMessage(content=state["spotify_wrapped_response"])
                state["messages"].append(wrapped_response)
            else:
                final_response = wrapped_llm.invoke(state["messages"])
                state["messages"].append(final_response)
        except Exception as e:
            print(f"[Wrapped Agent] Final response error: {e}")
            error_response = AIMessage(content="Sorry, I encountered an error generating your Spotify Wrapped.")
            state["messages"].append(error_response)
    
    return {"messages": state["messages"]}
