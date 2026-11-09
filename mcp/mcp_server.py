from mcp.server.mcpserver import MCPServer

from news_tools import (
    search_news,
    get_company_news,
    get_top_headlines,
)


mcp = MCPServer(
    "AI News Intelligence Server"
)


@mcp.tool()
def news_search(
    query: str,
    max_articles: int = 5
) -> str:

    """
    Search recent news about a topic,
    technology, person or event.
    """

    return search_news(
        query=query,
        max_articles=max_articles
    )


@mcp.tool()
def company_news(
    company: str,
    max_articles: int = 5
) -> str:

    """
    Search recent news about a specific company.
    """

    return get_company_news(
        company=company,
        max_articles=max_articles
    )


@mcp.tool()
def top_headlines(
    topic: str = "",
    max_articles: int = 5
) -> str:

    """
    Get current top headlines.
    """

    return get_top_headlines(
        topic=topic,
        max_articles=max_articles
    )


if __name__ == "__main__":

    mcp.run(
        transport="stdio"
    )
    
    
    