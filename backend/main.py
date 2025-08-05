from src.agent.main_graph import graph
from langchain_core.messages import HumanMessage
import asyncio

async def main():
    state = {"messages": []}
    config = {"configurable": {"thread_id": "user_session"}}
    print("DJ Spotify in the house! What's spinning? Ask me anything about your music! 🎵")
    while True:
        try:
            user_input = input("You: ")
            if user_input.strip().lower() in {"exit", "quit"}:
                print("Keep the music alive! Catch you on the flip side! 🎵")
                break

            state["messages"].append(HumanMessage(content=user_input))
            state = await graph.ainvoke(state, config=config)
            assistant_response = state["messages"][-1].content
            print("DJ Spotify:", assistant_response)

        except Exception as e:
            print("Error:", e)
            break

if __name__ == "__main__":
    asyncio.run(main())
