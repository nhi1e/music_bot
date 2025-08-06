from __future__ import annotations

from typing import Any, List
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.tavily_tool import search_music_info
from .base import BaseAgent

class WebAgent(BaseAgent):
    """Web search agent for general music information and facts"""

    @property
    def name(self) -> str:
        return 'web_agent'

    @property
    def description(self) -> str:
        return 'Searches the web for general music information and facts'

    @property
    def _prompt(self) -> str:
        return """You are a web search assistant that helps users find general music information and facts.
        
You can help users with:
- Finding information about artists, songs, and albums
- Music history and trivia
- Concert and tour information
- Music news and updates
- General music-related questions

Use the web search tool to find accurate and up-to-date information."""

    @property
    def _tools(self) -> List[Any]:
        return [search_music_info]

    def web_agent(self, state):
        """Process web search requests with state management"""
        messages = state["messages"]
        
        print(f"[Web Agent] Processing query with {len(messages)} messages")
        
        # Create LLM with tools bound
        web_llm = self._llm.bind_tools(self._tools)
        
        # Call LLM with tools
        response = web_llm.invoke(messages)
        state["messages"].append(response)
        
        # Handle tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Process all tool calls and collect responses
            tool_responses = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                tool_call_id = tool_call["id"]
                
                print(f"[Web Agent] Executing tool: {tool_name}({tool_args})")
                
                try:
                    # Execute the search_music_info tool
                    tool_output = search_music_info.invoke(tool_args or {})
                    
                    if not tool_output or str(tool_output).strip() == "":
                        tool_output = f"The {tool_name} tool completed but returned no results."
                    
                    print(f"[Web Agent] Tool output: {len(str(tool_output))} characters")
                    
                    tool_message = ToolMessage(
                        tool_call_id=tool_call_id,
                        content=str(tool_output)
                    )
                except Exception as e:
                    print(f"[Web Agent] Tool error: {e}")
                    tool_message = ToolMessage(
                        tool_call_id=tool_call_id,
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                
                tool_responses.append(tool_message)
            
            # Add all tool responses to messages
            state["messages"].extend(tool_responses)
            
            # Generate final response with tool results
            try:
                final_response = web_llm.invoke(state["messages"])
                state["messages"].append(final_response)
            except Exception as e:
                print(f"[Web Agent] Final response error: {e}")
                error_response = AIMessage(content="Sorry, I encountered an error processing your music search request.")
                state["messages"].append(error_response)
        
        return {"messages": state["messages"]}

# Create instance for backward compatibility
web_agent_instance = WebAgent()
web_agent = web_agent_instance.web_agent
