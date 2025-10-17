"""
Entry point for running AIM MCP server via `python -m aim_mcp_server`
"""

import asyncio
import sys
from .server import create_server


async def main() -> None:
    """Main entry point for the AIM MCP server."""
    server = create_server()
    
    # Run the server using stdio transport
    from mcp.server.stdio import stdio_server
    
    async with stdio_server(server.read_stream, server.write_stream) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        sys.exit(1)

