"""
Tool registry for MCP Toolbox.

Central registry for all available tools with their metadata and schemas.
This module defines tool interfaces that are exposed through the MCP protocol.
"""

from typing import Dict, Any, Callable
from tools import (
    yaml_to_json, json_to_yaml,
    base64_encode, sha256_hash,
    is_port_open, validate_url
)

# Tool metadata with JSON Schema definitions
# MCP uses JSON Schema to describe tool inputs
AVAILABLE_TOOLS = {
    "yaml_to_json": {
        "name": "yaml_to_json",
        "description": "Convert YAML string to JSON format. Useful for configuration file transformations and data interchange.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "yaml": {
                    "type": "string",
                    "description": "YAML string to convert to JSON"
                }
            },
            "required": ["yaml"]
        }
    },

    "json_to_yaml": {
        "name": "json_to_yaml",
        "description": "Convert JSON string to YAML format. YAML is more human-readable and commonly used in configuration files.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "json": {
                    "type": "string",
                    "description": "JSON string to convert to YAML"
                }
            },
            "required": ["json"]
        }
    },

    "base64_encode": {
        "name": "base64_encode",
        "description": "Encode text string to base64 format. Used for representing binary data in ASCII format.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Plain text to encode"
                }
            },
            "required": ["text"]
        }
    },

    "sha256_hash": {
        "name": "sha256_hash",
        "description": "Compute SHA256 cryptographic hash of text. Produces a 64-character hexadecimal hash string.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "Text to hash"
                }
            },
            "required": ["text"]
        }
    },

    "is_port_open": {
        "name": "is_port_open",
        "description": "Check if a TCP port is open on a host. Useful for service availability and network diagnostics. Times out after 3 seconds.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Hostname or IP address to check"
                },
                "port": {
                    "type": "integer",
                    "description": "Port number (1-65535)",
                    "minimum": 1,
                    "maximum": 65535
                }
            },
            "required": ["host", "port"]
        }
    },

    "validate_url": {
        "name": "validate_url",
        "description": "Validate URL format and structure. Checks for protocol, domain, and invalid characters.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to validate"
                }
            },
            "required": ["url"]
        }
    }
}

# Map tool names to their implementation functions
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "yaml_to_json": yaml_to_json,
    "json_to_yaml": json_to_yaml,
    "base64_encode": base64_encode,
    "sha256_hash": sha256_hash,
    "is_port_open": is_port_open,
    "validate_url": validate_url,
}


def get_tool_function(tool_name: str) -> Callable:
    """
    Get the implementation function for a tool by name.

    Args:
        tool_name: Name of the tool to retrieve

    Returns:
        Callable function that implements the tool

    Raises:
        KeyError: If tool name is not registered

    Example:
        >>> func = get_tool_function("yaml_to_json")
        >>> result = func("name: raj")
    """
    if tool_name not in TOOL_FUNCTIONS:
        raise KeyError(f"Tool '{tool_name}' not found in registry")

    return TOOL_FUNCTIONS[tool_name]