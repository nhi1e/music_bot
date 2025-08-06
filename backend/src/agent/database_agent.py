from __future__ import annotations

from typing import Any, List
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
import json
from ..tools.database_search_tool import search_music_by_vibe
from .base import BaseAgent

class DatabaseAgent(BaseAgent):
    """Database agent for music recommendations and vibe-based searches"""

    @property
    def name(self) -> str:
        return 'database_agent'

    @property
    def description(self) -> str:
        return 'Provides music recommendations and vibe-based searches from the music database'

    @property
    def _prompt(self) -> str:
        return """You are a music recommendation assistant that helps users find songs based on vibes and moods.
        
You can help users with:
- Finding music that matches specific vibes or moods
- Discovering new songs based on their preferences
- Providing music recommendations for different activities
- Searching the music database for similar tracks

Use the database search tool to find music that matches the user's requested vibe or mood."""

    @property
    def _tools(self) -> List[Any]:
        return [search_music_by_vibe]

    def database_agent(self, state):
        """Process database search requests with state management"""
        messages = state["messages"]
        
        print(f"[Database Agent] Processing query with {len(messages)} messages")
        
        # Create LLM with tools bound
        database_llm = self._llm.bind_tools(self._tools)
        
        # Call LLM with tools
        response = database_llm.invoke(messages)
        state["messages"].append(response)
        
        # Handle tool calls if present
        if hasattr(response, 'tool_calls') and response.tool_calls:
            # Process all tool calls and collect responses
            tool_responses = []
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("args", {})
                tool_call_id = tool_call["id"]
                
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
                    
                    tool_message = ToolMessage(
                        tool_call_id=tool_call_id,
                        content=str(tool_output)
                    )
                except Exception as e:
                    print(f"[Database Agent] Tool error: {e}")
                    tool_message = ToolMessage(
                        tool_call_id=tool_call_id,
                        content=f"Error executing {tool_name}: {str(e)}"
                    )
                
                tool_responses.append(tool_message)
            
            # Add all tool responses to messages
            state["messages"].extend(tool_responses)
            
            # Generate final response with tool results
            try:
                final_response = database_llm.invoke(state["messages"])
                state["messages"].append(final_response)
            except Exception as e:
                print(f"[Database Agent] Final response error: {e}")
                error_response = AIMessage(content="Sorry, I encountered an error processing your music recommendation request.")
                state["messages"].append(error_response)
        
        return {"messages": state["messages"]}

# Create instance for backward compatibility
database_agent_instance = DatabaseAgent()
database_agent = database_agent_instance.database_agent
