from __future__ import annotations

from typing import Any, List
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from ..tools.spotify import (
    get_playlist_names, get_playlists_with_details, get_playlist_tracks,
    get_recent_playlists, follow_playlist, unfollow_playlist, check_if_following_playlist,
    create_playlist, add_track_to_playlist, remove_track_from_playlist, search_and_add_to_playlist
)
from .base import BaseAgent

class PlaylistAgent(BaseAgent):
    """Spotify agent for playlist-related queries - playlist management and details"""

    @property
    def name(self) -> str:
        return 'playlist_agent'

    @property
    def description(self) -> str:
        return 'Handles Spotify playlist management and operations'

    @property
    def _prompt(self) -> str:
        return """
        You are a Spotify playlist assistant that helps users manage their playlists.
                
        You can help users with:
        - Viewing playlist names and details
        - Getting playlist tracks
        - Following and unfollowing playlists
        - Creating new playlists
        - Adding and removing tracks from playlists
        - Searching and adding songs to playlists

        Use the available tools to help users manage their Spotify playlists effectively."""

    @property
    def _tools(self) -> List[Any]:
        return [
            get_playlist_names, get_playlists_with_details, get_playlist_tracks,
            get_recent_playlists, follow_playlist, unfollow_playlist, check_if_following_playlist,
            create_playlist, add_track_to_playlist, remove_track_from_playlist, search_and_add_to_playlist
        ]

    def playlist_agent(self, state):
        """Process playlist-related Spotify requests with state management"""
        messages = state["messages"]
        
        print(f"[Playlist Agent] Processing query with {len(messages)} messages")
        
        # Create LLM with tools bound
        playlist_llm = self._llm.bind_tools(self._tools)
        
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
                    tool = next(t for t in self._tools if t.name == tool_name)
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

# Create instance for backward compatibility
playlist_agent_instance = PlaylistAgent()
playlist_agent = playlist_agent_instance.playlist_agent
