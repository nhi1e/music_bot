# Music Bot Query Routing Guide

This document explains how the music recommendation bot routes different types of queries to the appropriate tools based on user intent.

## Overview

The bot uses a classifier system that analyzes user queries and routes them to one of three main tool categories:

1. **Spotify Tools** - For user-specific Spotify data
2. **Vector Search Tools** - For music recommendations based on vibe/characteristics
3. **Web Search Tools** - For general music information and facts

## Tool Categories

### 🎵 Spotify Tools (`spotify`)

**Purpose**: Handle queries about the user's personal Spotify data and account interactions.

**When used**:

- Queries containing personal pronouns (`my`, `user`, `current user`)
- Requests for user-specific Spotify data
- Playlist management operations
- Profile and following operations

**Examples that route to Spotify**:

- ✅ "What are my top tracks this month?"
- ✅ "Show me my playlists"
- ✅ "What did I listen to recently?"
- ✅ "My saved tracks"
- ✅ "My top artists"
- ✅ "Recently played songs"
- ✅ "Follow this artist"
- ✅ "Get my playlist tracks"

**Available Spotify Functions**:

- `get_top_tracks()` - User's most played tracks
- `get_top_artists()` - User's most played artists
- `get_recently_played()` - Recently played tracks
- `get_playlist_names()` - User's playlist names
- `get_playlist_tracks()` - Tracks from specific playlist
- `get_saved_tracks()` - User's liked/saved songs
- `search_tracks()` - Search Spotify catalog
- `search_artist_info()` - Artist information and top tracks
- `follow_artist()` - Follow an artist
- `unfollow_artist()` - Unfollow an artist

### 🔍 Vector Search Tools (`vector`)

**Purpose**: Provide music recommendations based on musical characteristics, mood, vibe, or similarity to specific songs.

**When used**:

- Descriptive music characteristics (energy, mood, tempo)
- Similarity requests ("like", "similar to")
- Genre-specific recommendations with characteristics
- Vibe-based music discovery

**Examples that route to Vector Search**:

- ✅ "Give me chill but danceable music"
- ✅ "Happy indie tracks with low energy"
- ✅ "Songs similar to Bohemian Rhapsody by Queen"
- ✅ "Music like Hotel California"
- ✅ "Energetic electronic songs"
- ✅ "Sad acoustic tracks"
- ✅ "Upbeat songs for working out"
- ✅ "Mellow jazz for studying"
- ✅ "Fast tempo rock music"
- ✅ "Instrumental ambient music"

**Vector Search Features**:

- **Local Database Search**: Uses Word2Vec embeddings and audio features from local dataset
- **Spotify Search Integration**: When specific songs aren't found locally, automatically searches Spotify
- **Genre Filtering**: Can filter by specific genres (k-pop, rock, jazz, etc.)
- **Popularity Queries**: Handles requests for popular songs within genres
- **Audio Feature Matching**: Matches based on danceability, energy, valence, acousticness, etc.

**Similarity Pattern Recognition**:

- "similar to [song/artist]"
- "like [song] by [artist]"
- "songs like [reference]"
- "music like [reference]"
- "sounds like [reference]"
- "reminds me of [reference]"

### 🌐 Web Search Tools (`web`)

**Purpose**: Retrieve general music information, artist facts, music history, and educational content.

**When used**:

- Educational queries about music
- Artist biographies and facts
- Music theory and history
- Genre explanations
- General music information

**Examples that route to Web Search**:

- ✅ "What is ambient music?"
- ✅ "Who is Drake?"
- ✅ "Tell me about jazz history"
- ✅ "What instruments are used in rock music?"
- ✅ "Biography of The Beatles"
- ✅ "Explain music theory"
- ✅ "What genre is this artist?"
- ✅ "History of hip-hop"
- ✅ "Awards won by Taylor Swift"

**Web Search Functions**:

- `search_music_info()` - Uses Tavily API for comprehensive music information

## Classification Logic

### Priority Order

1. **Spotify Keywords** (Highest Priority)

   - Triggers: `my`, `top tracks`, `recently played`, `saved tracks`, `playlist`, etc.
   - Always routes to Spotify tools when personal data is requested

2. **Similarity Patterns** (High Priority)

   - Regex patterns: `similar to .+`, `like .+ by .+`, `songs like .+`
   - Routes to vector search for song-based recommendations

3. **Vector Keywords** (Medium Priority)

   - Musical characteristics: `chill`, `upbeat`, `energetic`, `mellow`, `acoustic`
   - Mood descriptors: `happy`, `sad`, `peaceful`, `intense`
   - Routes to vector search for vibe-based discovery

4. **Web Keywords** (Lower Priority)

   - Information queries: `what is`, `who is`, `tell me about`, `explain`
   - Educational content: `history`, `biography`, `facts about`

5. **Default Fallback**
   - Routes to web search for safety when intent is unclear

### Special Cases

**Genre + Characteristics**:

- "Happy pop songs" → Vector (recommendation)
- "What is pop music?" → Web (educational)

**Artist Queries**:

- "My top artists" → Spotify (personal data)
- "Songs like Taylor Swift" → Vector (similarity-based recommendation)
- "Who is Taylor Swift?" → Web (biographical information)

**Song Requests**:

- "Play my saved songs" → Spotify (user library)
- "Energetic songs for gym" → Vector (characteristic-based)
- "What songs did The Beatles write?" → Web (factual information)

## Vector Search Behavior

### Local Database vs Spotify Search

The vector search tool intelligently handles different scenarios:

1. **Song Found Locally**:

   - Uses vector similarity with local embeddings
   - Returns recommendations based on audio features and text similarity

2. **Song Not Found Locally**:

   - Automatically searches Spotify for the reference song
   - Returns Spotify search results as recommendations
   - Includes audio features when available

3. **Fallback Behavior**:
   - If Spotify search fails, falls back to text-based vector search
   - Uses song/artist names as search terms for similarity matching

### Genre Filtering

- Automatically detects genre mentions in queries
- Filters local database by genre when specified
- Supports genres: k-pop, pop, rock, jazz, hip-hop, electronic, country, classical, etc.

### Popularity Queries

- Detects popularity keywords: `popular`, `top`, `hit`, `chart`, `trending`
- When combined with genre, returns most popular songs in that genre
- Sorts by popularity score rather than similarity

## Example Query Flows

### Personal Spotify Data

```
User: "What are my top songs this month?"
→ Classifier: Detects "my" and "top" keywords
→ Route: spotify
→ Tool: get_top_tracks(time_range="short_term")
→ Result: User's personal top tracks from Spotify
```

### Vibe-Based Recommendation

```
User: "Give me chill but danceable music"
→ Classifier: Detects "chill" and "danceable" characteristics
→ Route: vector
→ Tool: search_music_by_vibe()
→ Process: Vector similarity search using audio features
→ Result: Songs matching chill + danceable characteristics
```

### Song Similarity (Song in Database)

```
User: "Songs like Hotel California by Eagles"
→ Classifier: Detects "songs like" similarity pattern
→ Route: vector
→ Tool: search_music_by_vibe()
→ Process: Find "Hotel California" in local DB, use its embedding
→ Result: Songs similar to Hotel California from local database
```

### Song Similarity (Song NOT in Database)

```
User: "Songs like Bad Habit by Steve Lacy"
→ Classifier: Detects "songs like" similarity pattern
→ Route: vector
→ Tool: search_music_by_vibe()
→ Process: Song not found locally → Search Spotify for "Bad Habit Steve Lacy"
→ Result: Spotify search results for that song/artist
```

### General Music Information

```
User: "What is lo-fi music?"
→ Classifier: Detects "what is" information query
→ Route: web
→ Tool: search_music_info()
→ Process: Tavily API search for lo-fi music information
→ Result: Educational content about lo-fi genre
```

## Configuration

### Required Environment Variables

- `SPOTIFY_CLIENT_ID` - For Spotify API access
- `SPOTIFY_CLIENT_SECRET` - For Spotify API access
- `SPOTIFY_REDIRECT_URI` - For Spotify OAuth
- `TAVILY_API_KEY` - For web search functionality

### Dataset Requirements

- Local music dataset at `backend/data/dataset.csv`
- Required columns: track_name, artists, audio features (danceability, energy, valence, etc.)
- Automatically preprocessed and embedded on startup

## Error Handling

### Spotify API Errors

- Authentication issues → Prompt user to reconnect Spotify
- Rate limiting → Retry with backoff
- No results → Inform user, suggest alternatives

### Vector Search Errors

- Dataset not loaded → Error message about dataset
- No embeddings → Fall back to text search
- Spotify search fails → Use local text-based search

### Web Search Errors

- Tavily API unavailable → Inform user, suggest Spotify features
- No results found → Provide generic response
- Network timeout → Retry once, then fail gracefully

## Performance Considerations

- **Vector Search**: Fast for local database queries (~100ms)
- **Spotify Search**: Dependent on API latency (~500-1000ms)
- **Web Search**: Dependent on Tavily API (~1-2s)
- **Embeddings**: Generated once at startup, cached in memory
- **Audio Features**: Retrieved on-demand for Spotify results

This routing system ensures users get the most relevant and accurate responses based on their query intent while providing comprehensive music discovery and information capabilities.
