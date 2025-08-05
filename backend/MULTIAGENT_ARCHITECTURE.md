# Multiagent Music Recommendation System

This system has been migrated from a single agent architecture to a multiagent system for better organization and scalability.

## Architecture Overview

### Main Entry Point: `main_graph.py`

- **Location**: `/backend/src/agent/main_graph.py`
- **Role**: Main coordinator and entry point for the entire system
- **Features**:
  - DJ Spotify system prompt and personality
  - Memory system ("remember" keyword handling)
  - Conversational response handling
  - Query routing to specialized agents

### Agent Structure

#### 1. Main Router

- Routes queries to appropriate specialized systems
- Handles memory and conversational elements
- Returns: `"spotify"`, `"web"`, `"database"`, or `"conversation_handled"`

#### 2. Spotify Subgraph

A nested graph that further routes Spotify-related queries:

**Spotify Router** (`spotify_router.py`)

- Routes to specialized Spotify agents
- Returns: `"playlist"`, `"artist"`, `"song"`, or `"wrapped"`

**Specialized Spotify Agents**:

- **Playlist Agent** (`playlist_agent.py`) - Playlist management and details
- **Artist Agent** (`artist_agent.py`) - Artist info, following, top artists
- **Song Agent** (`song_agent.py`) - Track searches, top tracks, recommendations
- **Wrapped Agent** (`wrapped_agent.py`) - Spotify Wrapped generation

#### 3. Web Agent (`web_agent.py`)

- Handles general music information queries
- Uses Tavily web search for music facts and artist information

#### 4. Database Agent (`database_agent.py`)

- Handles music recommendations based on vibe/mood
- Uses internal music database for similarity search

## Tool Distribution

### Spotify Tools

Split across specialized agents based on functionality:

**Song Agent Tools**:

- `get_top_tracks`
- `get_recently_played`
- `search_tracks`
- `get_saved_tracks`
- `get_recommendations_by_track`

**Artist Agent Tools**:

- `get_top_artists`
- `search_artist_info`
- `get_followed_artists`
- `follow_artist`
- `unfollow_artist`
- `check_if_following_artist`

**Playlist Agent Tools**:

- `get_playlist_names`
- `get_playlists_with_details`
- `get_playlist_tracks`
- `get_recent_playlists`
- `follow_playlist`
- `unfollow_playlist`
- `check_if_following_playlist`

**Wrapped Agent Tools**:

- `generate_spotify_wrapped`

### Non-Spotify Tools

**Web Agent Tools**:

- `search_music_info`

**Database Agent Tools**:

- `search_music_by_vibe`

## Key Features

### 1. Enhanced Error Handling

Each agent now includes:

- Tool execution error handling
- Response validation
- Fallback error messages
- Detailed logging

### 2. Memory System

- "remember" keyword triggers memory storage
- User preferences are stored and maintained
- System messages preserve context

### 3. Conversational Flow

- Natural conversation handling
- Casual responses don't force tool usage
- Music-focused engagement

### 4. Special Handling

- **Spotify Wrapped**: Preserves original JSON for frontend processing
- **Database Search**: Handles "specific_song_not_found" errors gracefully
- **Classification Safety**: Prevents hallucination by forcing tool usage

## Migration Notes

### Files Updated

1. **Entry Point**: `main_graph.py` is now the main entry point (not `agent.py`)
2. **Server Files**: Updated imports in `main.py`, `server.py`, and `src/api/server.py`
3. **All Agents**: Enhanced with proper tool handling and error management
4. **Import Paths**: Fixed relative imports throughout the agent system

### Benefits of Multiagent Architecture

1. **Modularity**: Each agent focuses on specific functionality
2. **Scalability**: Easy to add new agents or modify existing ones
3. **Maintainability**: Clear separation of concerns
4. **Performance**: Reduced tool overhead per agent
5. **Debugging**: Better error isolation and logging

## Usage

### Running the System

```bash
# Terminal interface
python main.py

# API server
python server.py
```

### Testing

```bash
# Test the multiagent system
python test_multiagent.py
```

The system maintains the same external interface while providing a much more organized and scalable internal architecture.
