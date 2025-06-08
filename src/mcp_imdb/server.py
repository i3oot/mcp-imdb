import asyncio
import json
import os
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.routing import Mount
import uvicorn
import logging
from mcp_imdb.tools import search_imdb, get_movie_details, get_actor_details, search_people

# Configure logging
logger = logging.getLogger("mcp_imdb_server")

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("mcp-imdb")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    """
    return []

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="search-imdb",
            description="Search IMDB for movies, TV shows, or other content using Cinemagoer.",
            arguments=[
                types.PromptArgument(
                    name="query",
                    description="Search query for IMDB",
                    required=True,
                ),
                types.PromptArgument(
                    name="content_type",
                    description="Type of content to search for (movie, tv, person)",
                    required=False,
                ),
                types.PromptArgument(
                    name="limit",
                    description="Maximum number of results to return (default: 10)",
                    required=False,
                )
            ],
        ),
        types.Prompt(
            name="get-movie-details",
            description="Get details about a movie from IMDB using Cinemagoer.",
            arguments=[
                types.PromptArgument(
                    name="imdb_id",
                    description="IMDB ID (with or without 'tt' prefix)",
                    required=True,
                )
            ],
        ),
        types.Prompt(
            name="get-actor-details",
            description="Get details about an actor or actress from IMDB using Cinemagoer.",
            arguments=[
                types.PromptArgument(
                    name="person_id",
                    description="IMDB person ID (with or without 'nm' prefix)",
                    required=True,
                )
            ],
        ),
        types.Prompt(
            name="search-people",
            description="Search for actors, actresses, directors, and other people on IMDB using Cinemagoer.",
            arguments=[
                types.PromptArgument(
                    name="query",
                    description="Search query for people on IMDB",
                    required=True,
                ),
                types.PromptArgument(
                    name="limit",
                    description="Maximum number of results to return (default: 10)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name not in ["search-imdb", "get-movie-details", "trending-movies", "get-actor-details", "search-people"]:
        raise ValueError(f"Unknown prompt: {name}")

    arguments = arguments or {}
    
    if name == "search-imdb":
        query = arguments.get("query", "")
        content_type = arguments.get("content_type", "")
        limit = arguments.get("limit", "10")
        
        content_type_text = f" (content type: {content_type})" if content_type else ""
        limit_text = f" (limit: {limit})" if limit != "10" else ""
        
        return types.GetPromptResult(
            description="Search IMDB for movies, TV shows, or other content using Cinemagoer.",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here is the search query: {query}{content_type_text}{limit_text}\n\n"
                    ),
                )
            ],
        )
    elif name == "get-movie-details":
        imdb_id = arguments.get("imdb_id", "")
        
        return types.GetPromptResult(
            description="Get details about a movie from IMDB using Cinemagoer.",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here is the IMDB ID: {imdb_id}\n\n"
                    ),
                )
            ],
        )
    elif name == "get-actor-details":
        person_id = arguments.get("person_id", "")
        
        return types.GetPromptResult(
            description="Get details about an actor or actress from IMDB using Cinemagoer.",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Here is the IMDB person ID: {person_id}\n\n"
                    ),
                )
            ],
        )
    elif name == "search-people":
        query = arguments.get("query", "")
        limit = arguments.get("limit", "10")
        limit_text = f" (limit: {limit})" if limit != "10" else ""
        
        return types.GetPromptResult(
            description="Search for actors, actresses, directors, and other people on IMDB using Cinemagoer.",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"Search for people on IMDB: {query}{limit_text}\n\n"
                    ),
                )
            ],
        )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="search-imdb",
            description="Search IMDB for movies, TV shows, or other content using Cinemagoer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for IMDB"},
                    "content_type": {
                        "type": "string", 
                        "description": "Type of content to search for", 
                        "enum": ["movie", "tv", "person"]
                    },
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return", 
                        "default": 10
                    }
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get-movie-details",
            description="Get details about a movie from IMDB using Cinemagoer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "imdb_id": {"type": "string", "description": "IMDB ID (with or without 'tt' prefix)"},
                },
                "required": ["imdb_id"],
            },
        ),
        types.Tool(
            name="get-trending-movies",
            description="Get trending movies from IMDB using Cinemagoer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return", 
                        "default": 10
                    }
                },
                "required": [],
            },
        ),
        types.Tool(
            name="get-actor-details",
            description="Get details about an actor or actress from IMDB using Cinemagoer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "person_id": {"type": "string", "description": "IMDB person ID (with or without 'nm' prefix)"},
                },
                "required": ["person_id"],
            },
        ),
        types.Tool(
            name="search-people",
            description="Search for actors, actresses, directors, and other people on IMDB using Cinemagoer.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query for people on IMDB"},
                    "limit": {
                        "type": "integer", 
                        "description": "Maximum number of results to return", 
                        "default": 10
                    }
                },
                "required": ["query"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    try:
        if name not in ["search-imdb", "get-movie-details", "get-actor-details", "search-people"]:
            raise ValueError(f"Unknown tool: {name}")


        # Extract query parameter based on tool name
        query = None
        content_type = None
        limit = 10  # Default limit
        person_id = None
        
        if name == "search-imdb":
            query = arguments.get("query")
            content_type = arguments.get("content_type")
            limit = int(arguments.get("limit", 10))
        elif name == "get-movie-details":
            query = arguments.get("imdb_id")
        elif name == "get-actor-details":
            person_id = arguments.get("person_id")
        elif name == "search-people":
            query = arguments.get("query")
            limit = int(arguments.get("limit", 10))

        # Validate required parameters
        if (not query and name not in ["get-actor-details"]) or \
           (not person_id and name == "get-actor-details"):
            raise ValueError(f"Missing required parameter for {name}")

        # Update server state if query exists
        if query:
            notes["name"] = query
        elif person_id:
            notes["name"] = person_id

        # Execute the appropriate tool
        if name == "search-imdb":
            results = await search_imdb(query, content_type, limit)
        elif name == "get-movie-details":
            results = await get_movie_details(query)
        elif name == "get-actor-details":
            results = await get_actor_details(person_id)
        elif name == "search-people":
            results = await search_people(query, limit)

        return [
            types.TextContent(
                type="text",
                text=json.dumps(results.model_dump() if hasattr(results, "model_dump") else 
                               [r.model_dump() for r in results], indent=2),
            )
        ]
    except ValueError as e:
        # Handle validation errors
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": "Validation Error", "message": str(e)}, indent=2),
            )
        ]
    except RuntimeError as e:
        # Handle runtime errors (API failures, etc.)
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": "Runtime Error", "message": str(e)}, indent=2),
            )
        ]
    except Exception as e:
        # Handle unexpected errors
        logger.exception(f"Unexpected error in handle_call_tool: {str(e)}")
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": "Server Error", "message": "An unexpected error occurred"}, indent=2),
            )
        ]

async def main() -> None:
    """Entry point for running the server.

    The transport protocol can be selected using the ``MCP_TRANSPORT``
    environment variable. Supported values are ``STDIO`` (default) and
    ``HTTP``. When ``HTTP`` is selected, the server is started using
    Streamable HTTP on the port specified by the ``PORT`` environment
    variable (default ``8000``).
    """

    transport = os.getenv("MCP_TRANSPORT", "STDIO").upper()

    if transport == "HTTP":
        session_manager = StreamableHTTPSessionManager(app=server)

        async def handle_streamable_http(scope, receive, send):
            await session_manager.handle_request(scope, receive, send)

        app = Starlette(
            routes=[Mount("/", app=handle_streamable_http)],
            lifespan=lambda starlette_app: session_manager.run(),
        )

        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=int(os.getenv("PORT", "8000")),
            log_level="info",
        )
        server_obj = uvicorn.Server(config)
        await server_obj.serve()
    else:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="mcp-imdb",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
