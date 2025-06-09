import json
import os
import logging

import mcp.types as types
from fastmcp import FastMCP

from mcp_imdb.tools import (
    search_imdb,
    get_movie_details,
    get_actor_details,
    search_people,
)

logger = logging.getLogger("mcp_imdb_server")

notes: dict[str, str] = {}

mcp = FastMCP("mcp-imdb")

@mcp.tool
async def search_imdb_tool(
    query: str,
    content_type: str | None = None,
    limit: int = 10,
) -> list[types.TextContent]:
    """Search IMDB and return results as JSON text."""
    notes["name"] = query
    results = await search_imdb(query, content_type, limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-movie-details")
async def get_movie_details_tool(imdb_id: str) -> list[types.TextContent]:
    """Fetch movie details and return them as JSON text."""
    notes["name"] = imdb_id
    result = await get_movie_details(imdb_id)
    return [types.TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))]

@mcp.tool(name="get-actor-details")
async def get_actor_details_tool(person_id: str) -> list[types.TextContent]:
    """Fetch actor details and return them as JSON text."""
    notes["name"] = person_id
    result = await get_actor_details(person_id)
    return [types.TextContent(type="text", text=json.dumps(result.model_dump(), indent=2))]

@mcp.tool(name="search-people")
async def search_people_tool(query: str, limit: int = 10) -> list[types.TextContent]:
    """Search IMDB for people and return the results as JSON text."""
    notes["name"] = query
    results = await search_people(query, limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

async def main() -> None:
    """Run the MCP server with the configured transport."""
    transport = os.getenv("MCP_TRANSPORT", "stdio").lower()
    port = int(os.getenv("PORT", "8000"))

    if transport == "http":
        await mcp.run_async("streamable-http", host="0.0.0.0", port=port)
    elif transport == "sse":
        await mcp.run_async("sse", host="0.0.0.0", port=port)
    else:
        await mcp.run_async("stdio")
