"""
MCP HTTP SSE Server Implementation using Official SDK.

This server uses the official MCP Python SDK's SseServerTransport
which is required for compatibility with MCP Inspector and other clients.

Usage:
    pip install mcp starlette uvicorn
    python server/http_server_fixed.py

Then use Inspector:
    npx @modelcontextprotocol/inspector --config inspector-config.json

inspector-config.json:
{
  "mcpServers": {
    "toolbox-sse": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
"""

import asyncio
import logging
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware.cors import CORSMiddleware

# Official MCP Python SDK
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

# Import our tool registry
from registry import AVAILABLE_TOOLS, get_tool_function

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-sse-server")

# Create MCP Server instance
mcp_server = Server("mcp-toolbox")

# Create SSE transport
# The "/messages" parameter is the endpoint path for client->server messages
sse_transport = SseServerTransport("/messages")


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """
    List all available tools.

    This is called by MCP clients to discover available tools.
    """
    logger.info("Listing tools")

    tools = []
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        tools.append(Tool(
            name=tool_info["name"],
            description=tool_info["description"],
            inputSchema=tool_info["inputSchema"]
        ))

    logger.info(f"Returning {len(tools)} tools")
    return tools


@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """
    Execute a tool.

    Args:
        name: Tool name
        arguments: Tool arguments

    Returns:
        List of TextContent with results
    """
    logger.info(f"Calling tool: {name}")
    logger.debug(f"Arguments: {arguments}")

    # Validate tool exists
    if name not in AVAILABLE_TOOLS:
        raise ValueError(f"Tool '{name}' not found")

    # Get and execute tool function
    tool_func = get_tool_function(name)

    try:
        # Execute tool (handle both sync and async)
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**arguments)
        else:
            result = tool_func(**arguments)

        logger.info(f"Tool {name} executed successfully")

        # Return as TextContent
        import json
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]

    except Exception as e:
        logger.error(f"Tool execution error: {e}", exc_info=True)
        raise


async def handle_sse(request):
    """
    Handle SSE endpoint.

    This establishes the server->client SSE connection and runs the MCP server.
    """
    logger.info("New SSE connection")

    async with sse_transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as streams:
        # Run the MCP server with the connected streams
        await mcp_server.run(
            streams[0],  # read stream
            streams[1],  # write stream
            mcp_server.create_initialization_options()
        )


async def handle_messages(request):
    """
    Handle POST messages from client.

    This is the client->server communication channel.
    """
    logger.info("Received message")
    await sse_transport.handle_post_message(
        request.scope,
        request.receive,
        request._send
    )


async def health_check(request):
    """Health check endpoint."""
    from starlette.responses import JSONResponse
    return JSONResponse({
        "status": "healthy",
        "server": "mcp-toolbox",
        "transport": "sse"
    })


# Create Starlette application
app = Starlette(
    debug=True,
    routes=[
        Route("/sse", endpoint=handle_sse),
        Route("/messages", endpoint=handle_messages, methods=["POST"]),
        Route("/health", endpoint=health_check),
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def main():
    """Start the server."""
    logger.info("Starting MCP SSE server on http://0.0.0.0:8000")
    logger.info("SSE endpoint: http://0.0.0.0:8000/sse")
    logger.info("Messages endpoint: http://0.0.0.0:8000/messages")
    logger.info("Health check: http://0.0.0.0:8000/health")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()