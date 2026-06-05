from langchain_mcp_adapters.client import MultiServerMCPClient

# Professional Pattern: LangChain MCP Adapters design the client to be stateless by default.
# When you fetch tools via `client.get_tools()`, each tool is returned with its connection
# configuration, and a fresh temporary session is created and closed automatically *on each tool call*.
# No persistent global connections, cache, or shutdown handlers are needed.


async def get_mcp_tools():
    """
    Fetches the weather and news tools from the MCP server.

    Each tool automatically manages its own session lifecycle when invoked.
    """
    client = MultiServerMCPClient(
        {
            "weather-news-tools": {
                "url": "http://localhost:8000/mcp/sse",
                "transport": "sse",
            }
        }
    )
    return await client.get_tools()
