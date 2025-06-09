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
    get_top_movies,
    get_top_tv,
    get_popular_movies,
    get_popular_tv,
    get_bottom_movies,
    get_top_indian_movies,
    get_boxoffice_movies,
    get_top_movies_by_genres,
    get_top_tv_by_genres,
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

@mcp.tool(name="get-top-movies")
async def get_top_movies_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb Top 250 movies."""
    results = await get_top_movies(limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-top-tv")
async def get_top_tv_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb Top 250 TV shows."""
    results = await get_top_tv(limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-popular-movies")
async def get_popular_movies_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb popular movies."""
    results = await get_popular_movies(limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-popular-tv")
async def get_popular_tv_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb popular TV shows."""
    results = await get_popular_tv(limit)
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

@mcp.tool(name="get-bottom-movies")
async def get_bottom_movies_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb Bottom 100 movies."""
    results = await get_bottom_movies(limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-top-indian-movies")
async def get_top_indian_movies_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb Top 250 Indian movies."""
    results = await get_top_indian_movies(limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-boxoffice-movies")
async def get_boxoffice_movies_tool(limit: int = 10) -> list[types.TextContent]:
    """Return IMDb box office movies."""
    results = await get_boxoffice_movies(limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-top-movies-by-genres")
async def get_top_movies_by_genres_tool(genres: str, limit: int = 10) -> list[types.TextContent]:
    """Return top movies filtered by genres."""
    results = await get_top_movies_by_genres(genres, limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

@mcp.tool(name="get-top-tv-by-genres")
async def get_top_tv_by_genres_tool(genres: str, limit: int = 10) -> list[types.TextContent]:
    """Return top TV shows filtered by genres."""
    results = await get_top_tv_by_genres(genres, limit)
    return [types.TextContent(type="text", text=json.dumps(results.model_dump(), indent=2))]

