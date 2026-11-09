import asyncio
from langchain_core.messages import HumanMessage
from mcp import Client
from graph import (
    create_mcp_server_parameters,
    get_mcp_tools,
    build_graph,
)
async def main():

    print()
    print("=" * 70)
    print("          AI NEWS INTELLIGENCE AGENT")
    print("=" * 70)
    print()
    print("Technology Stack")
    print("----------------")
    print("Python")
    print("Qwen 2.5 3B")
    print("Ollama")
    print("LangChain")
    print("LangGraph")
    print("Tool Calling")
    print("MCP")
    print("News API")

    print()
    print("Starting MCP server...")

    server_parameters = (
        create_mcp_server_parameters()
    )

    async with Client(
        server_parameters
    ) as mcp_client:

        print(
            "✓ MCP server connected"
        )

        tools = await get_mcp_tools(
            mcp_client
        )

        graph = build_graph(
            tools
        )

        print()
        print(
            "✓ LangGraph compiled successfully"
        )

        print()
        print("=" * 70)
        print(
            "Ask ANY news-related question."
        )
        print(
            "Type 'exit' to stop."
        )
        print("=" * 70)

        while True:

            try:

                query = input(
                    "\nAsk your question:\n> "
                ).strip()

            except (
                KeyboardInterrupt,
                EOFError
            ):

                print(
                    "\nExiting..."
                )

                break

            if query.lower() in {
                "exit",
                "quit"
            }:

                print(
                    "\nGoodbye!"
                )

                break

            if not query:

                print(
                    "Please enter a question."
                )

                continue

            print()
            print(
                "🤖 AI is thinking..."
            )

            try:

                result = await graph.ainvoke(
                    {
                        "messages": [
                            HumanMessage(
                                content=query
                            )
                        ]
                    }
                )

                final_message = (
                    result["messages"][-1]
                )

                print()
                print("-" * 70)
                print("AI RESPONSE")
                print("-" * 70)

                print(
                    final_message.content
                )

                print("-" * 70)

            except Exception as error:

                print()
                print("❌ ERROR")
                print(error)

                print()
                print(
                    "Please check:"
                )
                print(
                    "1. Ollama is running"
                )
                print(
                    "2. Qwen model exists"
                )
                print(
                    "3. News API key is valid"
                )
                print(
                    "4. Internet is available"
                )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
    
    
    
    
    
    