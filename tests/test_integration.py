import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

@pytest.mark.asyncio
async def test_server_integration():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp-imdb"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
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