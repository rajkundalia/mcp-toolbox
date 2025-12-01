"""
Format conversion tools for MCP Toolbox.

Provides bidirectional conversion between YAML and JSON formats.
These tools are useful for configuration file transformations and
data interchange between systems using different formats.
"""

import json
import yaml
from typing import Dict, Any


def yaml_to_json(yaml_string: str) -> Dict[str, Any]:
    """
    Convert YAML string to JSON string.

    This tool parses YAML input and converts it to formatted JSON output.
    Useful for converting configuration files or transforming data between
    formats commonly used in DevOps and configuration management.

    Args:
        yaml_string: Valid YAML string to convert

    Returns:
        Dictionary containing:
        - json: Formatted JSON string representation

    Raises:
        yaml.YAMLError: If the input is not valid YAML

    Example:
        >>> yaml_to_json("name: raj\\nrole: engineer")
        {'json': '{\\n  "name": "raj",\\n  "role": "engineer"\\n}'}
    """
    try:
        # Parse YAML string into Python object
        data = yaml.safe_load(yaml_string)

        # Convert to formatted JSON with 2-space indentation
        json_string = json.dumps(data, indent=2)

        return {"json": json_string}

    except yaml.YAMLError as e:
        # Re-raise as a clear error for MCP error handling
        raise ValueError(f"Invalid YAML input: {str(e)}")


def json_to_yaml(json_string: str) -> Dict[str, Any]:
    """
    Convert JSON string to YAML string.

    This tool parses JSON input and converts it to YAML output.
    YAML is often more human-readable and used extensively in
    configuration files (Kubernetes, Docker Compose, etc.).

    Args:
        json_string: Valid JSON string to convert

    Returns:
        Dictionary containing:
        - yaml: YAML string representation

    Raises:
        json.JSONDecodeError: If the input is not valid JSON

    Example:
        >>> json_to_yaml('{"name": "raj", "role": "engineer"}')
        {'yaml': 'name: raj\\nrole: engineer\\n'}
    """
    try:
        # Parse JSON string into Python object
        data = json.loads(json_string)

        # Convert to YAML with default flow style (block style)
        yaml_string = yaml.dump(data, default_flow_style=False, sort_keys=False)

        return {"yaml": yaml_string}

    except json.JSONDecodeError as e:
        # Re-raise as a clear error for MCP error handling
        raise ValueError(f"Invalid JSON input: {str(e)}")