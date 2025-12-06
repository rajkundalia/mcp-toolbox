"""
MCP Client Example Usage.

Demonstrates how to connect to and use an MCP server from a client application.
Shows both STDIO and HTTP SSE transport methods.

This file serves as a reference implementation for building MCP clients.
"""

import asyncio
import json
import sys

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

    # Summary
    print("\n" * 2)
    print("=" * 60)
    print(" Summary")
    print("=" * 60)
    print(f"STDIO Client: {'✓ Passed' if stdio_success else '✗ Failed'}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)