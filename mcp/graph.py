import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from pydantic import BaseModel, Field

from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama

from langgraph.graph import (
    StateGraph,
    START,
    END,
)

from langgraph.prebuilt import (
    ToolNode,
    tools_condition,
)

from mcp import (
    Client,
    StdioServerParameters,
)

from schemas import AgentState


load_dotenv()


MODEL_NAME = "qwen2.5:3b-instruct"


SYSTEM_PROMPT = """
You are an AI News Intelligence Agent.

Your job is to answer news questions using current
information retrieved through MCP tools.

AVAILABLE TOOLS

1. news_search
Use for current news about:
- technology
- AI
- science
- events
- people
- general topics

2. company_news
Use when the user asks about a specific company.

Examples:
- NVIDIA
- Google
- Microsoft
- Apple
- Tesla
- Amazon

3. top_headlines
Use for current general headlines, especially India.

TOOL SELECTION RULES

- Current/latest/recent/today/this week questions MUST use a tool.
- Company-specific questions MUST use company_news.
- Topic questions MUST use news_search.
- General India headlines MUST use top_headlines.
- Never invent current news.
- Never claim an article says something unless the tool result supports it.

AFTER TOOL RESULTS

Do NOT simply copy the raw tool output.

Instead:

1. Identify the most relevant articles.
2. Remove unrelated information.
3. Summarize the important developments.
4. Give 3-5 concise bullet points when possible.
5. Mention the source for each important point.
6. Include publication date when available.
7. If no relevant articles are found, clearly say so.
8. Do not invent missing details.

RESPONSE FORMAT

For current news:

📰 Latest News

1. Headline
   Source: Source Name
   Summary: One or two sentences.

2. Headline
   Source: Source Name
   Summary: One or two sentences.

3. Headline
   Source: Source Name
   Summary: One or two sentences.

Keep the answer concise.

For general knowledge questions that do not require
current information, answer directly without using
a news tool.
"""


class NewsSearchInput(BaseModel):
    query: str = Field(
        description="Topic or keyword to search for"
    )

    max_articles: int = Field(
        default=5,
        description="Maximum number of articles"
    )


class CompanyNewsInput(BaseModel):
    company: str = Field(
        description="Company name"
    )

    max_articles: int = Field(
        default=5,
        description="Maximum number of articles"
    )


class HeadlinesInput(BaseModel):
    topic: str = Field(
        default="",
        description="Optional topic"
    )

    max_articles: int = Field(
        default=5,
        description="Maximum number of articles"
    )


def create_mcp_server_parameters():

    server_path = Path(
        __file__
    ).with_name(
        "mcp_server.py"
    )

    environment = os.environ.copy()

    return StdioServerParameters(
        command=sys.executable,
        args=[
            str(server_path)
        ],
        env=environment,
    )


async def mcp_result_to_text(result):

    if result.is_error:
        return (
            f"MCP tool error: "
            f"{result.content}"
        )

    text_parts = []

    for block in result.content:

        if hasattr(block, "text"):
            text_parts.append(
                block.text
            )

    if text_parts:
        return "\n".join(
            text_parts
        )

    if result.structured_content:
        return str(
            result.structured_content
        )

    return str(
        result.content
    )


def create_news_search_tool(
    mcp_client
):

    async def execute(
        query: str,
        max_articles: int = 5
    ):

        print(
            f"\n🔧 TOOL CALL → news_search({query})"
        )

        result = await mcp_client.call_tool(
            "news_search",
            {
                "query": query,
                "max_articles": max_articles,
            }
        )

        return await mcp_result_to_text(
            result
        )

    return StructuredTool.from_function(
        coroutine=execute,
        name="news_search",
        description=(
            "Search recent news about a "
            "topic, technology, person or event."
        ),
        args_schema=NewsSearchInput,
    )


def create_company_news_tool(
    mcp_client
):

    async def execute(
        company: str,
        max_articles: int = 5
    ):

        print(
            f"\n🔧 TOOL CALL → company_news({company})"
        )

        result = await mcp_client.call_tool(
            "company_news",
            {
                "company": company,
                "max_articles": max_articles,
            }
        )

        return await mcp_result_to_text(
            result
        )

    return StructuredTool.from_function(
        coroutine=execute,
        name="company_news",
        description=(
            "Search recent news about a "
            "specific company."
        ),
        args_schema=CompanyNewsInput,
    )


def create_headlines_tool(
    mcp_client
):

    async def execute(
        topic: str = "",
        max_articles: int = 5
    ):

        print(
            f"\n🔧 TOOL CALL → top_headlines"
        )

        result = await mcp_client.call_tool(
            "top_headlines",
            {
                "topic": topic,
                "max_articles": max_articles,
            }
        )

        return await mcp_result_to_text(
            result
        )

    return StructuredTool.from_function(
        coroutine=execute,
        name="top_headlines",
        description=(
            "Get current top headlines "
            "from India."
        ),
        args_schema=HeadlinesInput,
    )


async def get_mcp_tools(
    mcp_client
):

    mcp_result = await mcp_client.list_tools()

    print()
    print(
        "MCP server tools discovered:"
    )

    for tool in mcp_result.tools:

        print(
            f"  ✓ {tool.name}"
        )

    tools = [
        create_news_search_tool(
            mcp_client
        ),
        create_company_news_tool(
            mcp_client
        ),
        create_headlines_tool(
            mcp_client
        ),
    ]

    return tools

def build_graph(langchain_tools):

    llm = ChatOllama(
        model=MODEL_NAME,
        temperature=0,
        num_predict=220,
        num_ctx=2048,
        keep_alive="10m",
    )

    llm_with_tools = llm.bind_tools(langchain_tools)

    async def agent_node(state: AgentState):

        response = await llm_with_tools.ainvoke(
            [
                ("system", SYSTEM_PROMPT),
                *state["messages"],
            ]
        )

        return {
            "messages": [response]
        }

    builder = StateGraph(AgentState)

    builder.add_node(
        "agent",
        agent_node,
    )

    builder.add_node(
        "tools",
        ToolNode(
            langchain_tools,
            handle_tool_errors=True,
        ),
    )

    builder.add_edge(
        START,
        "agent",
    )

    builder.add_conditional_edges(
        "agent",
        tools_condition,
    )

    builder.add_edge(
        "tools",
        "agent",
    )

    return builder.compile()






