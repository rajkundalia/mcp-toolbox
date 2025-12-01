"""
Text processing tools for MCP Toolbox.

Provides utilities for encoding text and computing cryptographic hashes.
These are commonly used for data transmission, storage, and verification.
"""

import base64
import hashlib
from typing import Dict, Any


def base64_encode(text: str) -> Dict[str, Any]:
    """
    Encode text string to base64 format.

    Base64 encoding is used to represent binary data in ASCII string format.
    Common use cases include:
    - Embedding binary data in JSON/XML
    - Transmitting data over text-only channels
    - Basic obfuscation (not encryption!)

    Args:
        text: Plain text string to encode

    Returns:
        Dictionary containing:
        - encoded: Base64-encoded string

    Example:
        >>> base64_encode("hello world")
        {'encoded': 'aGVsbG8gd29ybGQ='}
    """
    # Convert string to bytes, encode to base64, convert back to string
    text_bytes = text.encode('utf-8')
    encoded_bytes = base64.b64encode(text_bytes)
    encoded_string = encoded_bytes.decode('utf-8')

    return {"encoded": encoded_string}


def sha256_hash(text: str) -> Dict[str, Any]:
    """
    Compute SHA256 hash of text string.

    SHA256 is a cryptographic hash function that produces a 256-bit (32-byte)
    hash value, typically rendered as a 64-character hexadecimal string.

    Properties:
    - Deterministic: Same input always produces same output
    - One-way: Cannot reverse the hash to get original input
    - Collision-resistant: Extremely unlikely two inputs produce same hash

    Common uses:
    - Password storage (with salt)
    - File integrity verification
    - Digital signatures
    - Blockchain applications

    Args:
        text: Text string to hash

    Returns:
        Dictionary containing:
        - hash: 64-character hexadecimal hash string

    Example:
        >>> sha256_hash("hello world")
        {'hash': 'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'}
    """
    # Convert string to bytes and compute SHA256 hash
    text_bytes = text.encode('utf-8')
    hash_object = hashlib.sha256(text_bytes)
    hash_hex = hash_object.hexdigest()

    return {"hash": hash_hex}