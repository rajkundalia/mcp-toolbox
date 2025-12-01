"""
Network utility tools for MCP Toolbox.

Provides tools for network diagnostics and URL validation.
These tools help verify connectivity and validate network resources.
"""

import asyncio
from typing import Dict, Any
from urllib.parse import urlparse


async def is_port_open(host: str, port: int) -> Dict[str, Any]:
    """
    Check if a TCP port is open on a given host.

    This tool attempts to establish a TCP connection to the specified
    host and port. It's useful for:
    - Service availability checking
    - Network diagnostics
    - Pre-deployment validation

    Implementation uses async I/O for efficient non-blocking operations,
    which is important for MCP servers handling multiple requests.

    Args:
        host: Hostname or IP address to check (e.g., "localhost", "192.168.1.1")
        port: Port number (1-65535)

    Returns:
        Dictionary containing:
        - open: Boolean indicating if port is accessible

    Note:
        - Timeout is set to 3 seconds
        - Returns {"open": false} on timeout or connection failure
        - Port validation is performed (must be 1-65535)

    Example:
        >>> await is_port_open("localhost", 80)
        {'open': True}
        >>> await is_port_open("example.com", 9999)
        {'open': False}
    """
    # Validate port range
    if not (1 <= port <= 65535):
        raise ValueError(f"Port must be between 1 and 65535, got {port}")

    try:
        # Use asyncio to open a connection with timeout
        # This is non-blocking and won't freeze the server
        await asyncio.wait_for(
            asyncio.open_connection(host, port),
            timeout=3.0
        )
        return {"open": True}

    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        # Any connection failure means port is not open/accessible
        return {"open": False}


def validate_url(url: str) -> Dict[str, Any]:
    """
    Validate URL format and structure.

    Performs basic URL validation checking for:
    - Valid protocol (scheme)
    - Domain/netloc presence
    - No whitespace characters

    This is NOT a security validation tool. It only checks basic format.
    For production use, additional validation would be needed:
    - DNS resolution
    - SSL certificate validation
    - Content availability
    - Security scanning

    Args:
        url: URL string to validate

    Returns:
        Dictionary containing:
        - valid: Boolean indicating if URL is valid
        - reason: (Optional) String explaining why URL is invalid

    Example:
        >>> validate_url("https://example.com/path")
        {'valid': True}
        >>> validate_url("not a url")
        {'valid': False, 'reason': 'Missing protocol (http:// or https://)'}
    """
    # Check for whitespace (always invalid in URLs)
    if ' ' in url or '\t' in url or '\n' in url:
        return {
            "valid": False,
            "reason": "URL contains whitespace characters"
        }

    try:
        # Parse URL into components
        parsed = urlparse(url)

        # Check for protocol/scheme (http, https, ftp, etc.)
        if not parsed.scheme:
            return {
                "valid": False,
                "reason": "Missing protocol (http:// or https://)"
            }

        # Check for domain/netloc (the host part)
        if not parsed.netloc:
            return {
                "valid": False,
                "reason": "Missing domain name"
            }

        # Basic validation passed
        return {"valid": True}

    except Exception as e:
        # Catch any parsing errors
        return {
            "valid": False,
            "reason": f"URL parsing error: {str(e)}"
        }