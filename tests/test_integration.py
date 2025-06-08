import pytest
from fastmcp.client.client import ClientSession
from fastmcp.client.transports import StdioTransport

@pytest.mark.asyncio
async def test_server_integration():
    transport = StdioTransport(command="uv", args=["run", "mcp-imdb"])

    async with transport.connect_session() as session:
            # Test initialization
            await session.initialize()
            
            # Test tools listing
            tools_result = await session.list_tools()
            assert len(tools_result.tools) > 0
            
            # Test search functionality
            result = await session.call_tool(
                "search-imdb",
                arguments={"query": "Inception"}
            )
            assert result is not None 