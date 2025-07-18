# Music Recommendation Bot

An AI-powered music recommendation system with a conversational interface. Combines Spotify API, vector search, and web search to provide personalized music discovery.

## Features

- Conversational AI chatbot for music recommendations
- Spotify integration for personalized recommendations
- Vector similarity search for music discovery
- Web search for music information
- React frontend
- FastAPI backend with LangGraph agent

## Quick Start

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file with your API keys:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
OPENAI_API_KEY=your_openai_key
```

Run the backend:

```bash
python main.py          # CLI mode
python run.py server    # Web server mode
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Architecture

### Backend (`/backend`)

- **FastAPI server** with REST endpoints
- **LangGraph agent** for conversation flow
- **Multiple search tools**: Spotify API, vector search, web search
- **RAG evaluation** framework for quality assessment

### Frontend (`/frontend`)

- **React + TypeScript** application
- **Tailwind CSS** for styling
- **Vite** for development and building

## API Endpoints

- `GET /` - Health check
- `POST /chat` - Send message to chatbot
- `GET /health` - System status

## Development

Run both frontend and backend in development mode:

```bash
# Terminal 1 - Backend
cd backend && python run.py server

# Terminal 2 - Frontend
cd frontend && npm run dev
```

## Project Structure

```
backend/           # Python FastAPI backend
├── src/core/     # Core business logic
├── src/tools/    # LangChain tools
├── src/api/      # Web API
├── config/       # Configuration
└── evaluation/   # RAG evaluation

frontend/         # React TypeScript frontend
├── src/          # Source code
├── components/   # UI components
└── public/       # Static assets
```
