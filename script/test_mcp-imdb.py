import asyncio
import os
import logging
import signal
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Constants
TOOL_TIMEOUT = 30.0  # seconds

server_params = StdioServerParameters(
    command="uv", # Executable
    args=["run", "mcp-imdb"], # Optional command line arguments
    env=None # Optional environment variables
)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        #logging.FileHandler("/tmp/mcp_imdb_client_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("mcp_imdb_test")

async def run():
    logger.info("Starting MCP client test")
    
    # Start the MCP client
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            # Initialize the connection
            await session.initialize()
        
            # List available prompts
            prompts = await session.list_prompts()
            assert len(prompts.prompts) > 0

            # Get a prompt
            prompt = await session.get_prompt("get-movie-details", arguments={"imdb_id": "tt1375666"})
            assert prompt is not None

            # List available tools
            tools = await session.list_tools()
            assert len(tools.tools) > 0
            
            # Test search_movies tool
            try:
                logger.info("Testing search_movies tool")
                search_tool = next((tool for tool in tools.tools if tool.name == "search-imdb"), None)
                if search_tool:
                    logger.info("Calling search-imdb tool...")
                    result = await asyncio.wait_for(
                        session.call_tool(
                            "search-imdb",
                            arguments={"query": "Inception"}
                        ),
                        timeout=TOOL_TIMEOUT
                    )
                    logger.info("Search completed successfully")
                    
                    # Handle the result more carefully
                    if isinstance(result, dict):
                        logger.info(f"Number of results: {result.get('total_results', 0)}")
                        for idx, movie in enumerate(result.get('results', [])[:3], 1):
                            logger.info(f"Result {idx}:")
                            logger.info(f"  Title: {movie.get('title')}")
                            logger.info(f"  Year: {movie.get('year')}")
                            logger.info(f"  IMDB ID: {movie.get('imdb_id')}")
                    else:
                        logger.info(f"Result type: {type(result)}")
                        logger.info(f"Raw result: {str(result)[:200]}...")  # Log first 200 chars only
                else:
                    logger.error("search_movies tool not found")
            except asyncio.TimeoutError:
                logger.error(f"Search operation timed out after {TOOL_TIMEOUT} seconds")
            except Exception as e:
                logger.error(f"Error testing search_movies: {e}", exc_info=True)  # Add full traceback
            
            # Test get_movie tool
            try:
                logger.info("Testing get_movie tool:")
                movie_tool = next((tool for tool in tools.tools if tool.name == "get-movie-details"), None)
                if movie_tool:
                    logger.info("Calling get-movie-details tool...")
                    result = await asyncio.wait_for(
                        session.call_tool(
                            "get-movie-details",
                            arguments={"imdb_id": "tt1375666"}
                        ),
                        timeout=TOOL_TIMEOUT
                    )
                    logger.info("Movie details retrieved successfully")
                    
                    # Handle the movie result more carefully
                    if isinstance(result, dict):
                        logger.info("Movie details:")
                        logger.info(f"  Title: {result.get('title')}")
                        logger.info(f"  Year: {result.get('year')}")
                        logger.info(f"  Rating: {result.get('rating')}")
                        logger.info(f"  Director: {result.get('director')}")
                        if result.get('cast'):
                            logger.info(f"  Cast: {', '.join(result.get('cast', [])[:3])}...")
                    else:
                        logger.info(f"Result type: {type(result)}")
                        logger.info(f"Raw result: {str(result)[:200]}...")  # Log first 200 chars only
                else:
                    logger.error("get_movie tool not found")
            except asyncio.TimeoutError:
                logger.error(f"Get movie operation timed out after {TOOL_TIMEOUT} seconds")
            except Exception as e:
                logger.error(f"Error testing get_movie: {e}", exc_info=True)  # Add full traceback
            logger.info("Done")

def handle_signals():
    """Set up signal handlers for graceful shutdown."""
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(loop, sig)))

async def shutdown(loop, sig):
    """Cleanup tasks tied to the service's shutdown."""
    logger.info(f"Received exit signal {sig.name}")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    
    [task.cancel() for task in tasks]
    logger.info(f"Cancelling {len(tasks)} outstanding tasks")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()
            
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        handle_signals()
        loop.run_until_complete(run())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    finally:
        loop.close()
        logger.info("Shutdown complete") 
