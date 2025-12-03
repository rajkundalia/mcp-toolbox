"""
Tests for text processing tools.

Tests encoding and hashing functionality.
"""

import pytest
import sys

sys.path.insert(0, 'server')

from tools.text_tools import base64_encode, sha256_hash


class TestBase64Encode:
    """Test suite for base64_encode tool."""

    def test_simple_text(self):
        """Test basic text encoding."""
        result = base64_encode("hello")

        assert "encoded" in result
        assert result["encoded"] == "aGVsbG8="

    def test_empty_string(self):
        """Test encoding empty string."""
        result = base64_encode("")

        assert "encoded" in result
        assert result["encoded"] == ""

    def test_special_characters(self):
        """Test encoding text with special characters."""
        text = "Hello, World! @#$%"
        result = base64_encode(text)

        assert "encoded" in result
        # Verify it's valid base64 (contains only valid base64 chars)
        import base64
        decoded = base64.b64decode(result["encoded"]).decode('utf-8')
        assert decoded == text

    def test_unicode_text(self):
        """Test encoding Unicode text."""
        text = "Hello 世界 🌍"
        result = base64_encode(text)

        assert "encoded" in result
        # Verify round-trip
        import base64
        decoded = base64.b64decode(result["encoded"]).decode('utf-8')
        assert decoded == text

    def test_multiline_text(self):
        """Test encoding multiline text."""
        text = """Line 1
Line 2
Line 3"""
        result = base64_encode(text)

        assert "encoded" in result
        # Verify round-trip
        import base64
        decoded = base64.b64decode(result["encoded"]).decode('utf-8')
        assert decoded == text

    def test_deterministic(self):
        """Test that same input always produces same output."""
        text = "test message"
        result1 = base64_encode(text)
        result2 = base64_encode(text)

        assert result1["encoded"] == result2["encoded"]

    def test_different_inputs(self):
        """Test that different inputs produce different outputs."""
        result1 = base64_encode("hello")
        result2 = base64_encode("world")

        assert result1["encoded"] != result2["encoded"]


class TestSha256Hash:
    """Test suite for sha256_hash tool."""

    def test_simple_text(self):
        """Test basic text hashing."""
        result = sha256_hash("hello")

        assert "hash" in result
        # SHA256 produces 64 hex characters
        assert len(result["hash"]) == 64
        # Check it's hexadecimal
        assert all(c in "0123456789abcdef" for c in result["hash"])

    def test_known_hash(self):
        """Test against known SHA256 hash."""
        # "hello world" -> known hash
        result = sha256_hash("hello world")

        expected = "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        assert result["hash"] == expected

    def test_empty_string(self):
        """Test hashing empty string."""
        result = sha256_hash("")

        assert "hash" in result
        # Empty string has known hash
        expected = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        assert result["hash"] == expected

    def test_deterministic(self):
        """Test that same input always produces same hash."""
        text = "test message"
        result1 = sha256_hash(text)
        result2 = sha256_hash(text)

        assert result1["hash"] == result2["hash"]

    def test_different_inputs(self):
        """Test that different inputs produce different hashes."""
        result1 = sha256_hash("hello")
        result2 = sha256_hash("world")

        assert result1["hash"] != result2["hash"]

    def test_case_sensitive(self):
        """Test that hash is case-sensitive."""
        result1 = sha256_hash("Hello")
        result2 = sha256_hash("hello")

        assert result1["hash"] != result2["hash"]

    def test_unicode_text(self):
        """Test hashing Unicode text."""
        text = "Hello 世界"
        result = sha256_hash(text)

        assert "hash" in result
        assert len(result["hash"]) == 64

    def test_long_text(self):
        """Test hashing long text."""
        text = "a" * 10000
        result = sha256_hash(text)

        assert "hash" in result
        # Hash length is always 64 regardless of input length
        assert len(result["hash"]) == 64

    def test_special_characters(self):
        """Test hashing text with special characters."""
        text = "!@#$%^&*()_+-={}[]|:;\"'<>,.?/"
        result = sha256_hash(text)

        assert "hash" in result
        assert len(result["hash"]) == 64


class TestTextToolsIntegration:
    """Integration tests combining multiple text tools."""

    def test_encode_then_hash(self):
        """Test encoding then hashing the result."""
        text = "integration test"

        # Encode
        encoded_result = base64_encode(text)
        encoded_text = encoded_result["encoded"]

        # Hash the encoded text
        hash_result = sha256_hash(encoded_text)

        assert "hash" in hash_result
        assert len(hash_result["hash"]) == 64

    def test_hash_then_encode(self):
        """Test hashing then encoding the hash."""
        text = "test data"

        # Hash
        hash_result = sha256_hash(text)
        hash_value = hash_result["hash"]

        # Encode the hash
        encoded_result = base64_encode(hash_value)

        assert "encoded" in encoded_result
        # Verify round-trip
        import base64
        decoded = base64.b64decode(encoded_result["encoded"]).decode('utf-8')
        assert decoded == hash_value