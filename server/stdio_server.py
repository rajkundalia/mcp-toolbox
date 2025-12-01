"""
MCP STDIO Server Implementation.

STDIO (Standard Input/Output) Transport:
- Communication happens via stdin/stdout using JSON-RPC 2.0 protocol
- Server reads JSON-RPC requests from stdin
- Server writes JSON-RPC responses to stdout
- Logging MUST go to stderr (never stdout, which is reserved for protocol)

This is the simplest MCP transport - the server runs as a subprocess
and the parent process communicates by writing to its stdin and reading
from its stdout. This is how most MCP clients (including the Inspector)
launch and communicate with MCP servers.

Usage:
    python server/stdio_server.py

    # Or from another process:
    import subprocess
    proc = subprocess.Popen(
        ["python", "server/stdio_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
"""

import asyncio
import logging
import signal
import sys
import json
from typing import Any

# MCP SDK imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import our tool registry
from registry import AVAILABLE_TOOLS, get_tool_function

# Configure logging to stderr (stdout is reserved for JSON-RPC)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Critical: logs must go to stderr, not stdout
)
logger = logging.getLogger("mcp-stdio-server")

# Create MCP server instance
# The Server class handles JSON-RPC protocol details
app = Server("mcp-toolbox-stdio")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """
    Handler for MCP list_tools request.

    This method is called when a client wants to discover available tools.
    It returns metadata for all registered tools including names, descriptions,
    and input schemas.

    Returns:
        List of Tool objects with metadata for each available tool
    """
    logger.info("Received list_tools request")

    # Convert our registry format to MCP Tool objects
    tools = []
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        tools.append(Tool(
            name=tool_info["name"],
            description=tool_info["description"],
            inputSchema=tool_info["inputSchema"]
        ))

    logger.info(f"Returning {len(tools)} tools")
    return tools


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Handler for MCP call_tool request.

    This method is called when a client wants to execute a tool.
    It validates the tool exists, executes it with provided arguments,
    and returns the result in MCP format.

    Args:
        name: Name of the tool to execute
        arguments: Dictionary of tool arguments

    Returns:
        List containing a single TextContent object with the result

    Raises:
        ValueError: If tool doesn't exist or arguments are invalid

    MCP Error Codes:
        -32601 METHOD_NOT_FOUND: Tool doesn't exist
        -32602 INVALID_PARAMS: Invalid tool arguments
        -32603 INTERNAL_ERROR: Unexpected server error
    """
    logger.info(f"Received call_tool request: {name}")
    logger.debug(f"Arguments: {arguments}")

    try:
        # Check if tool exists in registry
        if name not in AVAILABLE_TOOLS:
            error_msg = f"Tool '{name}' not found"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # Get the tool implementation function
        tool_func = get_tool_function(name)

        # Execute the tool
        # Note: Some tools (like is_port_open) are async, others are sync
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**arguments)
        else:
            result = tool_func(**arguments)

        logger.info(f"Tool {name} executed successfully")
        logger.debug(f"Result: {result}")

        # MCP requires results to be wrapped in TextContent
        # We convert the result dict to a string representation
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except ValueError as e:
        # ValueError indicates invalid parameters (INVALID_PARAMS error)
        logger.error(f"Invalid parameters for {name}: {e}")
        raise

    except Exception as e:
        # Any other error is an internal server error
        logger.error(f"Internal error executing {name}: {e}", exc_info=True)
        raise RuntimeError(f"Internal error: {str(e)}")


async def main():
    """
    Main entry point for STDIO server.

    Sets up signal handlers for graceful shutdown and starts the server.
    The stdio_server() function handles all the JSON-RPC communication
    details - we just need to provide it with our Server instance.
    """
    logger.info("Starting MCP STDIO server")

    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("Server ready, waiting for requests on stdin...")

    # Start the STDIO server
    # This will:
    # 1. Read JSON-RPC requests from stdin
    # 2. Route them to appropriate handlers (@app.list_tools, @app.call_tool)
    # 3. Write JSON-RPC responses to stdout
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())