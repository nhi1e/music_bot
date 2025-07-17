#!/usr/bin/env python3
"""
Music Recommendation Bot - Entry Point
"""

import os
import sys
import argparse
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

def run_cli():
    """Run the CLI version of the bot"""
    from main import main
    import asyncio
    asyncio.run(main())

def run_server():
    """Run the web server"""
    import uvicorn
    from src.api.server import app
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )

def run_evaluation():
    """Run RAG evaluation"""
    print("🎵 Running Music RAG Evaluation...")
    print("Choose evaluation type:")
    print("1. Quick evaluation")
    print("2. Comprehensive analysis")
    print("3. Custom music metrics")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        os.system("cd evaluation && python quick_rag_eval.py")
    elif choice == "2":
        os.system("cd evaluation && python comprehensive_rag_analysis.py")
    elif choice == "3":
        os.system("cd evaluation && python music_rag_metrics.py")
    else:
        print("Invalid choice")

def setup_environment():
    """Setup the environment and check dependencies"""
    from config.settings import Config
    
    try:
        Config.validate()
        print("✅ Environment configuration is valid")
        return True
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("\n💡 Please check your .env file and ensure all required variables are set:")
        print("   - SPOTIFY_CLIENT_ID")
        print("   - SPOTIFY_CLIENT_SECRET")
        print("   - SPOTIFY_REDIRECT_URI")
        print("   - OPENAI_API_KEY")
        return False

def main():
    parser = argparse.ArgumentParser(description="Music Recommendation Bot")
    parser.add_argument(
        "mode",
        choices=["cli", "server", "eval", "setup"],
        help="Mode to run the application in"
    )
    
    args = parser.parse_args()
    
    if args.mode == "setup":
        setup_environment()
    elif args.mode == "cli":
        if setup_environment():
            run_cli()
    elif args.mode == "server":
        if setup_environment():
            run_server()
    elif args.mode == "eval":
        run_evaluation()

if __name__ == "__main__":
    main()
