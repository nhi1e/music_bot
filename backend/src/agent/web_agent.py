from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.tavily_tool import search_music_info

web_llm = ChatOpenAI(model="gpt-4o", temperature=0.7).bind_tools([search_music_info])

def web_agent(state):
    """Web agent for general music information using web search"""
    messages = state["messages"]
    
    print(f"[Web Agent] Processing query with {len(messages)} messages")
    
    # Call LLM with tools
    response = web_llm.invoke(messages)
    state["messages"].append(response)
    
    # Handle tool calls if present
    if hasattr(response, 'tool_calls') and response.tool_calls:
        for tool_call in response.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call.get("args", {})
            
            print(f"[Web Agent] Executing tool: {tool_name}({tool_args})")
            
            try:
                # Execute the search_music_info tool
                tool_output = search_music_info.invoke(tool_args or {})
                
                if not tool_output or str(tool_output).strip() == "":
                    tool_output = f"The {tool_name} tool completed but returned no results."
                
                print(f"[Web Agent] Tool output: {len(str(tool_output))} characters")
                
                # Add tool response
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=str(tool_output)
                    )
                )
            except Exception as e:
                print(f"[Web Agent] Tool error: {e}")
                state["messages"].append(
                    ToolMessage(
                        tool_call_id=tool_call["id"],
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                )
        
        # Generate final response with tool results
        try:
            final_response = web_llm.invoke(state["messages"])
            state["messages"].append(final_response)
        except Exception as e:
            print(f"[Web Agent] Final response error: {e}")
            error_response = AIMessage(content="Sorry, I encountered an error processing your music search request.")
            state["messages"].append(error_response)
    
    return {"messages": state["messages"]}
