# Music Recommendation Bot

An AI-powered music recommendation system using Spotify API, vector search, and web search.

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and add your API keys:

```bash
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
OPENAI_API_KEY=your_openai_api_key
```

## Usage

### CLI Mode

```bash
python main.py
```

### Web Server Mode

```bash
python run.py server
```

### Quick Setup

```bash
python run.py setup  # Validates environment
```

├── .spotify_cache # Spotify auth cache (auto-generated)
├── main.py # CLI entry point
├── requirements.txt # Production dependencies
└── README.md # This file

````

## Module Descriptions

### 📁 `src/core/` - Core Business Logic

- **`agent.py`**: Main RAG agent using LangGraph for conversation flow
- **`classifier.py`**: Classifies user queries into spotify/web/vector routes
- **`memory.py`**: Manages conversation memory and context
- **`schema.py`**: Pydantic models for data validation

### 📁 `src/api/` - Web API

- **`server.py`**: FastAPI application with REST endpoints

### 📁 `src/tools/` - LangChain Tools

- **`spotify_tool.py`**: Spotify API integration tools
- **`vector_search_tool.py`**: Music similarity search using embeddings
- **`tavily_tool.py`**: Web search for music information
- **`vector.py`**: Vector embedding utilities

### 📁 `config/` - Configuration

- **`settings.py`**: Centralized configuration management

### 📁 `evaluation/` - RAG Evaluation

- **`analyze_rag_results.py`**: Analyze RAGAs evaluation results
- **`comprehensive_rag_analysis.py`**: Detailed evaluation with insights
- **`evaluate_rag_with_ragas.py`**: Full RAGAs evaluation framework
- **`music_rag_metrics.py`**: Custom metrics for music recommendations
- **`quick_rag_eval.py`**: Quick evaluation for development

### 📁 `tests/` - Testing

- Various test files for different components
- Integration and end-to-end tests

### 📁 `scripts/` - Utility Scripts

- **`setup_spotify.py`**: Spotify API setup and configuration

## Running the Application

### CLI Interface

```bash
python main.py
````

### Web API Server

```bash
cd src/api
python server.py
```

### RAG Evaluation

```bash
cd evaluation
python quick_rag_eval.py        # Quick evaluation
python comprehensive_rag_analysis.py  # Detailed analysis
```

## 📦 Dependencies

### Production Dependencies (`requirements.txt`)

- Core application dependencies

### Evaluation Dependencies (`evaluation/evaluation_requirements.txt`)

- RAGAs and evaluation-specific dependencies

## 🔧 Configuration

1. Copy `.env.example` to `.env`
2. Fill in your API keys:
   - `SPOTIFY_CLIENT_ID`
   - `SPOTIFY_CLIENT_SECRET`
   - `SPOTIFY_REDIRECT_URI`
   - `OPENAI_API_KEY`
   - `TAVILY_API_KEY` (optional)

## Key Features

- **Multi-modal Music Search**: Spotify API, vector similarity, web search
- **Conversation Memory**: Maintains context across interactions
- **RAG Evaluation**: Comprehensive evaluation using RAGAs framework
- **Flexible API**: Both CLI and web interfaces
- **Modular Architecture**: Clean separation of concerns

## Evaluation Metrics

The system uses RAGAs (Retrieval-Augmented Generation Assessment) for evaluation:

- **Faithfulness**: How well answers are grounded in context
- **Answer Relevancy**: How well answers address questions
- **Context Precision**: Quality of retrieved context
- **Custom Music Metrics**: Domain-specific evaluation

## Import Structure

The reorganized structure uses relative imports:

```python
# Core modules
from src.core.agent import graph
from src.core.classifier import classify_query

# Tools
from src.tools.spotify_tool import get_top_tracks
from src.tools.vector_search_tool import search_music_by_vibe

# Configuration
from config.settings import config
```
