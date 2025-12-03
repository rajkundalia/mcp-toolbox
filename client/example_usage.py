"""
MCP Client Example Usage.

Demonstrates how to connect to and use an MCP server from a client application.
Shows both STDIO and HTTP SSE transport methods.

This file serves as a reference implementation for building MCP clients.
"""

import asyncio
import json
import subprocess
import sys
from typing import Optional

# MCP SDK imports for client
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def example_stdio_client():
    """
    Demonstrate STDIO transport client.

    STDIO Transport:
    1. Launch server as subprocess
    2. Communicate via stdin/stdout pipes
    3. Send JSON-RPC requests, receive responses
    4. Clean up subprocess on exit
    """
    print("=" * 60)
    print("MCP STDIO Client Example")
    print("=" * 60)

    # Define server parameters
    # The server will be launched as a subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["server/stdio_server.py"],
        env=None  # Inherit environment
    )

    print("\n1. Connecting to STDIO server...")

    try:
        # Connect to server using context manager for automatic cleanup
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                print("✓ Connected successfully\n")

                # Initialize connection
                await session.initialize()
                print("✓ Session initialized\n")

                # Step 1: List available tools
                print("2. Discovering available tools...")
                tools_result = await session.list_tools()

                print(f"✓ Found {len(tools_result.tools)} tools:\n")
                for tool in tools_result.tools:
                    print(f"  - {tool.name}: {tool.description}")

                # Step 2: Convert YAML to JSON
                print("\n3. Testing yaml_to_json tool...")
                yaml_input = """
name: John Doe
role: Engineer
skills:
  - Python
  - JavaScript
  - Docker
"""

                result = await session.call_tool(
                    "yaml_to_json",
                    arguments={"yaml": yaml_input.strip()}
                )

                print(f"Input YAML:\n{yaml_input}")
                print(f"Output JSON:\n{result.content[0].text}\n")

                # Step 3: Encode text to base64
                print("4. Testing base64_encode tool...")
                text = "Hello, MCP World!"

                result = await session.call_tool(
                    "base64_encode",
                    arguments={"text": text}
                )

                response = json.loads(result.content[0].text)
                print(f"Input: {text}")
                print(f"Encoded: {response['encoded']}\n")

                # Step 4: Compute SHA256 hash
                print("5. Testing sha256_hash tool...")
                text = "hello world"

                result = await session.call_tool(
                    "sha256_hash",
                    arguments={"text": text}
                )

                response = json.loads(result.content[0].text)
                print(f"Input: {text}")
                print(f"SHA256: {response['hash']}\n")

                # Step 5: Check if port is open
                print("6. Testing is_port_open tool...")

                result = await session.call_tool(
                    "is_port_open",
                    arguments={"host": "localhost", "port": 80}
                )

                response = json.loads(result.content[0].text)
                print(f"localhost:80 is {'open' if response['open'] else 'closed'}\n")

                # Step 6: Validate URL
                print("7. Testing validate_url tool...")
                test_urls = [
                    "https://example.com",
                    "not a url",
                    "ftp://files.example.com/file.txt"
                ]

                for url in test_urls:
                    result = await session.call_tool(
                        "validate_url",
                        arguments={"url": url}
                    )

                    response = json.loads(result.content[0].text)
                    status = "✓ Valid" if response['valid'] else "✗ Invalid"
                    reason = f" ({response.get('reason', '')})" if not response['valid'] else ""
                    print(f"  {url}: {status}{reason}")

                print("\n8. Testing error handling...")
                try:
                    # Try to call non-existent tool
                    await session.call_tool(
                        "nonexistent_tool",
                        arguments={}
                    )
                except Exception as e:
                    print(f"✓ Caught expected error: {type(e).__name__}")

                try:
                    # Try invalid YAML
                    await session.call_tool(
                        "yaml_to_json",
                        arguments={"yaml": "invalid: yaml: [[["}
                    )
                except Exception as e:
                    print(f"✓ Caught expected error: {type(e).__name__}")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)
    return True


async def example_http_client():
    """
    Demonstrate HTTP SSE transport client.

    HTTP SSE Transport Features:
    1. Server must be running separately (python server/http_server.py)
    2. SSE endpoint (GET /sse) for server-to-client streaming
    3. POST endpoint (/message) for client-to-server requests

    This example demonstrates the key difference: SSE allows the server
    to push updates to clients in real-time without polling.
    """
    print("=" * 60)
    print("MCP HTTP SSE Client Example")
    print("=" * 60)
    print("\nNote: Make sure HTTP server is running:")
    print("  python server/http_server.py")
    print()

    try:
        import aiohttp
    except ImportError:
        print("✗ aiohttp not installed. Install with: pip install aiohttp")
        return False

    base_url = "http://localhost:8000"
    sse_messages = []

    async def listen_to_sse(session):
        """
        Listen to SSE stream and collect messages.

        This demonstrates the server-to-client streaming capability
        that makes SSE different from simple HTTP POST/response.
        """
        try:
            async with session.get(f"{base_url}/sse") as response:
                print("📡 Connected to SSE stream (listening for server events)...\n")

                async for line in response.content:
                    line = line.decode('utf-8').strip()

                    if line.startswith('data:'):
                        # Extract JSON data from SSE message
                        data = line[5:].strip()
                        try:
                            message = json.loads(data)
                            sse_messages.append(message)

                            # Print server-pushed events
                            if message.get('type') == 'connection':
                                print(f"  📨 SSE Event: {message.get('message')}")
                            elif message.get('type') == 'tool_result':
                                print(f"  📨 SSE Event: Tool '{message.get('tool')}' executed")
                                print(f"     Result: {message.get('result')}")
                        except json.JSONDecodeError:
                            pass

                    # Stop after receiving a few messages
                    if len(sse_messages) >= 3:
                        break
        except Exception as e:
            print(f"  ℹ️  SSE connection closed: {e}")

    try:
        async with aiohttp.ClientSession() as http_session:
            print("1. Testing SSE streaming (the key feature)...")

            # Start SSE listener in background
            sse_task = asyncio.create_task(listen_to_sse(http_session))

            # Give SSE connection time to establish
            await asyncio.sleep(1)

            print("\n2. Testing list_tools endpoint...")

            # Send list_tools request via POST
            async with http_session.post(
                f"{base_url}/message",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1
                }
            ) as response:
                result = await response.json()
                tools = result['result']['tools']
                print(f"✓ Found {len(tools)} tools via POST\n")

            print("3. Testing call_tool endpoint (watch for SSE notification)...")

            # Call yaml_to_json tool via POST
            async with http_session.post(
                f"{base_url}/message",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "yaml_to_json",
                        "arguments": {"yaml": "name: test"}
                    },
                    "id": 2
                }
            ) as response:
                result = await response.json()
                print(f"✓ Tool executed via POST")
                print(f"  Result: {result['result']['content'][0]['text']}")

            # Give time for SSE notification to arrive
            await asyncio.sleep(0.5)

            print("\n4. Testing health endpoint...")
            async with http_session.get(f"{base_url}/health") as response:
                health = await response.json()
                print(f"✓ Server status: {health['status']}")
                print(f"  Active SSE connections: {health['active_connections']}")

            # Clean up SSE listener
            sse_task.cancel()
            try:
                await sse_task
            except asyncio.CancelledError:
                pass

            print("\n" + "=" * 60)
            print("Key Difference: SSE vs STDIO")
            print("=" * 60)
            print("✓ SSE allows server to PUSH updates to clients")
            print("✓ Multiple clients can receive the same events")
            print("✓ Useful for: monitoring, dashboards, collaborative tools")
            print(f"✓ Received {len(sse_messages)} server-pushed events")
            print("=" * 60)

    except aiohttp.ClientError as e:
        print(f"\n✗ Connection error: {e}")
        print("Make sure the HTTP server is running!")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 60)
    print("✓ HTTP client test completed!")
    print("=" * 60)
    return True


async def main():
    """
    Main entry point.

    Runs both STDIO and HTTP client examples.
    """
    print("\n" + "=" * 60)
    print(" MCP Toolbox - Client Examples")
    print("=" * 60 + "\n")

    # Run STDIO client example
    stdio_success = await example_stdio_client()

    print("\n" * 2)

    # Ask if user wants to test HTTP client
    try:
        response = input("Test HTTP client? (requires server running) [y/N]: ")
        if response.lower() == 'y':
            http_success = await example_http_client()
        else:
            print("Skipping HTTP client test.")
            http_success = True
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return

    # Summary
    print("\n" * 2)
    print("=" * 60)
    print(" Summary")
    print("=" * 60)
    print(f"STDIO Client: {'✓ Passed' if stdio_success else '✗ Failed'}")
    print(f"HTTP Client:  {'✓ Passed' if http_success else '✗ Failed'}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)