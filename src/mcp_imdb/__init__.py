import asyncio

# The server module is imported lazily in ``main`` to avoid import-time side
# effects during unit tests.

def main():
    """Main entry point for the package."""
    from . import server
    asyncio.run(server.main())

# Optionally expose other important items at package level
__all__ = ['main', 'server']
