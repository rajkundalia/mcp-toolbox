"""
Ollama Host Implementation for MCP Toolbox.

This host bridges Ollama LLMs with MCP tools, enabling the model to:
1. Understand available tools from MCP server
2. Decide when to use tools
3. Execute tools via MCP protocol
4. Incorporate tool results into responses

Architecture:
    User -> Host -> Ollama (tool decision) -> Host -> MCP Server (tool execution)
    -> Host -> Ollama (final response) -> User
"""

import asyncio
import json
import logging
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

import ollama
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ollama-host")


class OllamaHost:
    """
    Host that connects Ollama LLM with MCP tool server.

    The host maintains conversation state and orchestrates the interaction
    between the user, the LLM, and the MCP tools.
    """

    def __init__(self, config_path: str = "host/config.yaml"):
        """
        Initialize the host with configuration.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self._load_config(config_path)
        self.conversation_history = []
        self.mcp_session: Optional[ClientSession] = None
        self.available_tools = []

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded configuration from {config_path}")
                return config
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                'server': {'transport': 'stdio'},
                'ollama': {
                    'model': 'llama3',
                    'temperature': 0.7,
                    'timeout': 30
                }
            }

    async def initialize_mcp(self):
        """
        Initialize connection to MCP server.

        Launches STDIO server as subprocess and establishes connection.
        """
        logger.info("Initializing MCP connection...")

        # Setup server parameters based on transport type
        transport = self.config['server'].get('transport', 'stdio')

        if transport == 'stdio':
            server_params = StdioServerParameters(
                command="python",
                args=["server/stdio_server.py"],
                env=None
            )

            # Connect to STDIO server
            self.read_stream, self.write_stream = await stdio_client(server_params).__aenter__()
            self.mcp_session = ClientSession(self.read_stream, self.write_stream)
            await self.mcp_session.__aenter__()

        else:
            raise ValueError(f"Unsupported transport: {transport}")

        # Initialize session
        await self.mcp_session.initialize()
        logger.info("✓ MCP session initialized")

        # Discover available tools
        tools_result = await self.mcp_session.list_tools()
        self.available_tools = tools_result.tools
        logger.info(f"✓ Discovered {len(self.available_tools)} tools")

        for tool in self.available_tools:
            logger.info(f"  - {tool.name}")

    def _create_system_prompt(self) -> str:
        """
        Create system prompt that teaches the model about available tools.

        The system prompt is critical - it teaches the model:
        1. What tools are available
        2. When to use them
        3. How to format tool requests
        """
        tools_description = []

        for tool in self.available_tools:
            # Format tool information for the model
            tool_info = f"""
Tool: {tool.name}
Description: {tool.description}
Input Schema: {json.dumps(tool.inputSchema, indent=2)}
"""
            tools_description.append(tool_info)

        tools_text = "\n".join(tools_description)

        system_prompt = f"""You are a helpful assistant with access to tools. When a user's request requires using a tool, you should respond with a tool call.

Available Tools:
{tools_text}

To use a tool, respond with a JSON object in this exact format:
{{
  "tool": "tool_name",
  "arguments": {{
    "param1": "value1"
  }}
}}

IMPORTANT:
- Only output the JSON object, nothing else
- Use exact tool names and parameter names from the schemas
- After receiving tool results, provide a natural language response to the user

Examples:

User: "Convert this YAML to JSON: name: john"
Assistant: {{"tool": "yaml_to_json", "arguments": {{"yaml": "name: john"}}}}

User: "What's the base64 encoding of 'hello'?"
Assistant: {{"tool": "base64_encode", "arguments": {{"text": "hello"}}}}

If the request doesn't need a tool, just respond normally in natural language.
"""
        return system_prompt

    async def call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """
        Execute a tool via MCP protocol.

        Args:
            tool_name: Name of tool to execute
            arguments: Tool arguments

        Returns:
            Tool result as string
        """
        logger.info(f"Calling MCP tool: {tool_name}")
        logger.debug(f"Arguments: {arguments}")

        try:
            result = await self.mcp_session.call_tool(tool_name, arguments=arguments)

            # Extract text content from result
            if result.content and len(result.content) > 0:
                result_text = result.content[0].text
                logger.info(f"✓ Tool {tool_name} executed successfully")
                return result_text
            else:
                return json.dumps({"error": "No result returned"})

        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return json.dumps({"error": str(e)})

    def _parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """
        Parse LLM response for tool call.

        The model might return:
        1. Pure JSON tool call
        2. Text with embedded JSON
        3. Regular text (no tool call)

        Args:
            response: LLM response text

        Returns:
            Parsed tool call dict or None if not a tool call
        """
        # Try to find JSON in response
        response = response.strip()

        # Look for JSON object
        try:
            # Try parsing entire response as JSON
            data = json.loads(response)
            if isinstance(data, dict) and "tool" in data and "arguments" in data:
                return data
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from text
        import re
        json_pattern = r'\{[^{}]*"tool"[^{}]*"arguments"[^{}]*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if "tool" in data and "arguments" in data:
                    return data
            except json.JSONDecodeError:
                continue

        return None

    async def chat(self, user_message: str) -> str:
        """
        Process user message through Ollama with tool support.

        Flow:
        1. Send message to Ollama with tool descriptions
        2. Check if response contains tool call
        3. If yes: execute tool, send result back to Ollama
        4. Return final response to user

        Args:
            user_message: User's input message

        Returns:
            Final response to show user
        """
        logger.info(f"User: {user_message}")

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Create messages for Ollama including system prompt
        messages = [
                       {"role": "system", "content": self._create_system_prompt()}
                   ] + self.conversation_history

        # Get response from Ollama
        try:
            response = ollama.chat(
                model=self.config['ollama']['model'],
                messages=messages,
                options={
                    'temperature': self.config['ollama'].get('temperature', 0.7)
                }
            )

            assistant_message = response['message']['content']
            logger.info(f"Ollama: {assistant_message[:100]}...")

        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return f"Error: Failed to get response from Ollama. Is it running? ({e})"

        # Check if response contains a tool call
        tool_call = self._parse_tool_call(assistant_message)

        if tool_call:
            logger.info(f"Detected tool call: {tool_call['tool']}")

            # Execute the tool
            tool_result = await self.call_mcp_tool(
                tool_call['tool'],
                tool_call['arguments']
            )

            # Add tool interaction to history
            self.conversation_history.append({
                "role": "assistant",
                "content": f"[Tool Call: {tool_call['tool']}]"
            })

            self.conversation_history.append({
                "role": "user",
                "content": f"[Tool Result: {tool_result}]\n\nNow provide a natural language response to the user based on this result."
            })

            # Get final response from Ollama
            messages = [
                           {"role": "system", "content": self._create_system_prompt()}
                       ] + self.conversation_history

            try:
                final_response = ollama.chat(
                    model=self.config['ollama']['model'],
                    messages=messages,
                    options={
                        'temperature': self.config['ollama'].get('temperature', 0.7)
                    }
                )

                final_message = final_response['message']['content']

                # Add to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": final_message
                })

                return final_message

            except Exception as e:
                logger.error(f"Error getting final response: {e}")
                return f"Tool executed successfully, but error formatting response: {e}"

        else:
            # No tool call, just a regular response
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return assistant_message

    async def run_interactive(self):
        """
        Run interactive chat loop.

        User can type messages and get responses with automatic tool usage.
        """
        print("\n" + "=" * 60)
        print(" MCP Toolbox - Ollama Host")
        print("=" * 60)
        print(f"\nModel: {self.config['ollama']['model']}")
        print(f"Tools: {len(self.available_tools)} available")
        print("\nType 'quit' or 'exit' to end session")
        print("Type 'tools' to list available tools")
        print("Type 'clear' to clear conversation history")
        print("=" * 60 + "\n")

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                # Check for commands
                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye!")
                    break

                if user_input.lower() == 'tools':
                    print("\nAvailable Tools:")
                    for tool in self.available_tools:
                        print(f"  - {tool.name}: {tool.description}")
                    print()
                    continue

                if user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("\n✓ Conversation history cleared\n")
                    continue

                # Process message
                response = await self.chat(user_input)
                print(f"\nAssistant: {response}\n")

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit.")
                continue
            except EOFError:
                print("\n\nGoodbye!")
                break

    async def cleanup(self):
        """Clean up resources."""
        if self.mcp_session:
            await self.mcp_session.__aexit__(None, None, None)
        logger.info("✓ Cleaned up resources")


async def main():
    """Main entry point."""
    # Check if Ollama is available
    try:
        ollama.list()
    except Exception as e:
        print(f"\n✗ Error: Cannot connect to Ollama.")
        print(f"  Make sure Ollama is installed and running.")
        print(f"  Visit: https://ollama.ai")
        print(f"\n  Error details: {e}\n")
        sys.exit(1)

    # Create and initialize host
    host = OllamaHost()

    try:
        await host.initialize_mcp()
        await host.run_interactive()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        await host.cleanup()


if __name__ == "__main__":
    asyncio.run(main())