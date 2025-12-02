"""
MCP HTTP SSE Server Implementation.

HTTP SSE (Server-Sent Events) Transport:
- Server exposes HTTP endpoints for communication
- GET /sse: SSE endpoint for server-to-client streaming
- POST /message: Endpoint for client-to-server JSON-RPC requests
- Uses FastAPI framework for HTTP server

SSE vs WebSocket:
- SSE is unidirectional (server -> client only)
- Client sends requests via HTTP POST
- Simpler than WebSocket, works through most proxies
- Perfect for server notifications and updates

The SSE connection stays open and the server can push messages at any time.
Each SSE message must follow this format:
    data: <json content>\n\n
The double newline is critical - it marks the end of each message.

Usage:
    python server/http_server.py

Then connect clients to:
    - SSE: GET http://localhost:8000/sse
    - Messages: POST http://localhost:8000/message
"""

import asyncio
import json
import logging
from typing import Any, Dict
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import our tool registry
from registry import AVAILABLE_TOOLS, get_tool_function

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mcp-http-server")

# Store active SSE connections
# In production, you'd use a proper pub/sub system
active_connections: list[asyncio.Queue] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Handles startup and shutdown events.
    """
    logger.info("Starting HTTP SSE server")
    yield
    logger.info("Shutting down HTTP SSE server")


# Create FastAPI application
app = FastAPI(
    title="MCP Toolbox HTTP Server",
    description="MCP server with HTTP SSE transport",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for development
# In production, configure this properly with specific origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def sse_generator(queue: asyncio.Queue):
    """
    Generator for SSE events.

    Yields messages from the queue in SSE format.
    Each message must be formatted as:
        data: <content>\n\n

    The double newline (\n\n) is critical - it signals the end of an event.
    Browsers and SSE clients wait for this delimiter.

    Note: In production, implement periodic keepalive (e.g., every 30s) to prevent
    proxy timeouts, but only when no messages are being sent to avoid unnecessary delays.

    Args:
        queue: asyncio.Queue containing messages to send

    Yields:
        SSE-formatted messages
    """
    try:
        while True:
            # Wait for next message with timeout for keepalive
            try:
                message = await asyncio.wait_for(queue.get(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send keepalive comment to prevent connection timeout
                yield ": keepalive\n\n"
                continue

            if message is None:  # Shutdown signal
                break

            # Format as SSE: "data: <json>\n\n"
            # The double newline is REQUIRED by SSE specification
            yield f"data: {json.dumps(message)}\n\n"

    except asyncio.CancelledError:
        logger.info("SSE connection cancelled")
    finally:
        # Clean up connection
        if queue in active_connections:
            active_connections.remove(queue)


@app.get("/sse")
async def sse_endpoint():
    """
    Server-Sent Events endpoint.

    Establishes a long-lived HTTP connection for server-to-client streaming.
    The connection stays open and the server can push updates at any time.

    Returns:
        StreamingResponse with text/event-stream content type

    SSE Format:
        Each event is formatted as:
            data: <json>\n\n

        Comments (keepalive):
            : keepalive\n\n

    Connection Lifecycle:
        1. Client connects to GET /sse
        2. Server holds connection open
        3. Server pushes messages as they occur
        4. Client or server closes connection when done
    """
    logger.info("New SSE connection established")

    # Create a queue for this connection
    queue: asyncio.Queue = asyncio.Queue()
    active_connections.append(queue)

    # Send initial connection message
    await queue.put({
        "type": "connection",
        "status": "connected",
        "message": "SSE connection established"
    })

    # Return streaming response with SSE content type
    return StreamingResponse(
        sse_generator(queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable proxy buffering
        }
    )


@app.post("/message")
async def message_endpoint(request: Request):
    """
    JSON-RPC message endpoint.

    Accepts JSON-RPC 2.0 requests from clients and routes them to
    appropriate handlers (list_tools, call_tool, etc.).

    Why POST instead of SSE for client requests?
    - SSE is server->client only (unidirectional)
    - Client needs a separate channel to send requests
    - POST provides simple request/response pattern

    Args:
        request: FastAPI Request object containing JSON-RPC payload

    Returns:
        JSON-RPC response

    JSON-RPC Format:
        Request:
            {
                "jsonrpc": "2.0",
                "method": "tools/list" or "tools/call",
                "params": {...},
                "id": 1
            }

        Response:
            {
                "jsonrpc": "2.0",
                "result": {...},
                "id": 1
            }

        Error:
            {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32600,
                    "message": "Invalid Request"
                },
                "id": 1
            }
    """
    try:
        # Parse JSON-RPC request
        body = await request.json()
        logger.info(f"Received message: {body.get('method')}")

        method = body.get("method")
        params = body.get("params", {})
        request_id = body.get("id")

        # Route to appropriate handler
        if method == "tools/list":
            result = await handle_list_tools()
        elif method == "tools/call":
            result = await handle_call_tool(params)
        else:
            # Unknown method
            return create_error_response(
                request_id,
                -32601,  # METHOD_NOT_FOUND
                f"Method '{method}' not found"
            )

        # Return successful JSON-RPC response
        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        }

    except json.JSONDecodeError:
        return create_error_response(
            None,
            -32700,  # PARSE_ERROR
            "Invalid JSON"
        )

    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return create_error_response(
            body.get("id") if 'body' in locals() else None,
            -32603,  # INTERNAL_ERROR
            str(e)
        )


async def handle_list_tools() -> Dict[str, Any]:
    """
    Handle list_tools request.

    Returns metadata for all available tools.

    Returns:
        Dictionary with tools list
    """
    logger.info("Handling list_tools request")

    tools = []
    for tool_name, tool_info in AVAILABLE_TOOLS.items():
        tools.append({
            "name": tool_info["name"],
            "description": tool_info["description"],
            "inputSchema": tool_info["inputSchema"]
        })

    logger.info(f"Returning {len(tools)} tools")
    return {"tools": tools}


async def handle_call_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle call_tool request.

    Executes the specified tool with given arguments.

    Args:
        params: Dictionary containing:
            - name: Tool name
            - arguments: Tool arguments

    Returns:
        Dictionary with tool execution result

    Raises:
        ValueError: If tool not found or invalid parameters
    """
    tool_name = params.get("name")
    arguments = params.get("arguments", {})

    logger.info(f"Handling call_tool request: {tool_name}")
    logger.debug(f"Arguments: {arguments}")

    # Validate tool exists
    if tool_name not in AVAILABLE_TOOLS:
        raise ValueError(f"Tool '{tool_name}' not found")

    # Get and execute tool function
    tool_func = get_tool_function(tool_name)

    try:
        # Execute tool (handle both sync and async functions)
        if asyncio.iscoroutinefunction(tool_func):
            result = await tool_func(**arguments)
        else:
            result = tool_func(**arguments)

        logger.info(f"Tool {tool_name} executed successfully")

        # Broadcast result to all SSE connections
        for queue in active_connections:
            await queue.put({
                "type": "tool_result",
                "tool": tool_name,
                "result": result
            })

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, indent=2)
                }
            ]
        }

    except ValueError as e:
        # Invalid parameters
        logger.error(f"Invalid parameters: {e}")
        raise
    except Exception as e:
        # Internal error
        logger.error(f"Internal error: {e}", exc_info=True)
        raise RuntimeError(f"Internal error: {str(e)}")


def create_error_response(request_id: Any, code: int, message: str) -> Dict[str, Any]:
    """
    Create JSON-RPC error response.

    Args:
        request_id: Request ID from original request
        code: Error code (JSON-RPC standard codes)
        message: Error message

    Returns:
        JSON-RPC error response
    """
    return {
        "jsonrpc": "2.0",
        "error": {
            "code": code,
            "message": message
        },
        "id": request_id
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "active_connections": len(active_connections)
    }


def main():
    """Start the HTTP server."""
    logger.info("Starting HTTP SSE server on port 8000")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()