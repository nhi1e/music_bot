# Spotify Music Chatbot

A conversational AI chatbot that integrates with Spotify to help you explore your music preferences, discover new tracks, and get insights about your listening habits.

## Features

- 🎵 Get your top tracks (short-term, medium-term, long-term)
- 📝 View your playlists
- 🕐 See recently played tracks
- 🔍 Search for tracks on Spotify
- ❤️ View your saved/liked tracks
- 🌐 Get music information from the web
- 💭 Conversational memory across sessions

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Create Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click "Create App"
3. Fill in:
   - **App Name**: Your app name (e.g., "Music Chatbot")
   - **App Description**: Brief description
   - **Redirect URI**: `http://localhost:8080/callback`
   - **APIs used**: Web API
4. Save the app
5. Note down your **Client ID** and **Client Secret**

### 3. Configure Environment

1. Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```env
   SPOTIFY_CLIENT_ID=your_spotify_client_id_here
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here
   SPOTIFY_REDIRECT_URI=http://localhost:8080/callback
   OPENAI_API_KEY=your_openai_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

### 4. Test Spotify Setup

Run the setup script to test your Spotify connection:

```bash
python setup_spotify.py
```

This will:

- Verify your Spotify credentials
- Open a browser for Spotify authentication
- Test all API endpoints
- Create a cache file for future use

### 5. Run the Chatbot

```bash
python main.py
```

## Available Commands

Ask the chatbot questions like:

- "What are my top tracks?"
- "Show me my playlists"
- "What did I listen to recently?"
- "Search for songs by The Beatles"
- "What are my saved tracks?"
- "Tell me about jazz music" (web search)

## API Scopes Required

The app requests these Spotify scopes:

- `user-top-read` - Access top tracks and artists
- `playlist-read-private` - Access private playlists
- `user-read-recently-played` - Access recently played tracks
- `user-library-read` - Access saved tracks

## Troubleshooting

### Spotify Authentication Issues

1. **Invalid Redirect URI**: Make sure `http://localhost:8080/callback` is added to your Spotify app settings
2. **Invalid Client Credentials**: Double-check your Client ID and Secret in `.env`
3. **Scope Issues**: The app will request necessary permissions during first login

### Common Errors

- **"No module named 'spotipy'"**: Run `pip install -r requirements.txt`
- **"Invalid credentials"**: Check your `.env` file
- **"Redirect URI mismatch"**: Ensure redirect URI matches in both `.env` and Spotify Dashboard

## File Structure

```
backend/
├── main.py                 # Main chatbot entry point
├── setup_spotify.py        # Spotify setup and testing
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment file
├── .env                   # Your environment variables (create this)
└── app/
    ├── agent.py           # LangGraph agent with routing
    ├── memory.py          # In-memory conversation storage
    ├── schema.py          # Data models
    ├── classifier.py      # Query classification
    └── tools/
        ├── spotify_tool.py    # Spotify API tools
        └── tavily_tool.py     # Web search tools
```

## Development

The chatbot uses:

- **LangGraph** for conversation flow and agent routing
- **Spotipy** for Spotify Web API integration
- **OpenAI GPT-4** for natural language processing
- **Tavily** for web search capabilities
- **LangChain** for tool orchestration

## License

MIT License
