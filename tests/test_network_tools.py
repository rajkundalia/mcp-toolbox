"""
Tests for network utility tools.

Tests URL validation and port checking with mocks for network operations.
"""

import pytest
import asyncio
import sys

sys.path.insert(0, 'server')

from tools.network_tools import is_port_open, validate_url
from unittest.mock import patch, AsyncMock


class TestIsPortOpen:
    """Test suite for is_port_open tool."""

    @pytest.mark.asyncio
    async def test_port_validation_too_low(self):
        """Test that port numbers below 1 are rejected."""
        with pytest.raises(ValueError) as excinfo:
            await is_port_open("localhost", 0)

        assert "Port must be between 1 and 65535" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_port_validation_too_high(self):
        """Test that port numbers above 65535 are rejected."""
        with pytest.raises(ValueError) as excinfo:
            await is_port_open("localhost", 65536)

        assert "Port must be between 1 and 65535" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_valid_port_range(self):
        """Test valid port numbers are accepted."""
        # Mock the connection to avoid actual network calls
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
            mock_conn.return_value = (None, None)

            # Test minimum valid port
            result = await is_port_open("localhost", 1)
            assert result["open"] is True

            # Test maximum valid port
            result = await is_port_open("localhost", 65535)
            assert result["open"] is True

            # Test common port
            result = await is_port_open("localhost", 80)
            assert result["open"] is True

    @pytest.mark.asyncio
    async def test_connection_success(self):
        """Test successful connection returns open=True."""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
            mock_conn.return_value = (None, None)

            result = await is_port_open("example.com", 80)

            assert "open" in result
            assert result["open"] is True

    @pytest.mark.asyncio
    async def test_connection_refused(self):
        """Test refused connection returns open=False."""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
            mock_conn.side_effect = ConnectionRefusedError()

            result = await is_port_open("localhost", 9999)

            assert "open" in result
            assert result["open"] is False

    @pytest.mark.asyncio
    async def test_connection_timeout(self):
        """Test connection timeout returns open=False."""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
            mock_conn.side_effect = asyncio.TimeoutError()

            result = await is_port_open("example.com", 12345)

            assert "open" in result
            assert result["open"] is False

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test network errors return open=False."""
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
            mock_conn.side_effect = OSError("Network unreachable")

            result = await is_port_open("192.168.1.1", 22)

            assert "open" in result
            assert result["open"] is False


class TestValidateUrl:
    """Test suite for validate_url tool."""

    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        result = validate_url("http://example.com")

        assert result["valid"] is True
        assert "reason" not in result

    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        result = validate_url("https://example.com")

        assert result["valid"] is True

    def test_valid_url_with_path(self):
        """Test valid URL with path."""
        result = validate_url("https://example.com/path/to/resource")

        assert result["valid"] is True

    def test_valid_url_with_query(self):
        """Test valid URL with query parameters."""
        result = validate_url("https://example.com?param1=value1&param2=value2")

        assert result["valid"] is True

    def test_valid_url_with_fragment(self):
        """Test valid URL with fragment."""
        result = validate_url("https://example.com/page#section")

        assert result["valid"] is True

    def test_valid_url_with_port(self):
        """Test valid URL with explicit port."""
        result = validate_url("https://example.com:8080")

        assert result["valid"] is True

    def test_missing_protocol(self):
        """Test URL without protocol is invalid."""
        result = validate_url("example.com")

        assert result["valid"] is False
        assert "reason" in result
        assert "protocol" in result["reason"].lower()

    def test_missing_domain(self):
        """Test URL without domain is invalid."""
        result = validate_url("https://")

        assert result["valid"] is False
        assert "reason" in result
        assert "domain" in result["reason"].lower()

    def test_whitespace_in_url(self):
        """Test URL with whitespace is invalid."""
        result = validate_url("https://example .com")

        assert result["valid"] is False
        assert "reason" in result
        assert "whitespace" in result["reason"].lower()

    def test_tab_in_url(self):
        """Test URL with tab character is invalid."""
        result = validate_url("https://example\t.com")

        assert result["valid"] is False
        assert "whitespace" in result["reason"].lower()

    def test_newline_in_url(self):
        """Test URL with newline is invalid."""
        result = validate_url("https://example\n.com")

        assert result["valid"] is False
        assert "whitespace" in result["reason"].lower()

    def test_ftp_protocol(self):
        """Test FTP URLs are valid."""
        result = validate_url("ftp://ftp.example.com/file.txt")

        assert result["valid"] is True

    def test_file_protocol(self):
        """Test file:// URLs are valid."""
        result = validate_url("file:///path/to/file")

        assert result["valid"] is True

    def test_localhost_url(self):
        """Test localhost URLs are valid."""
        result = validate_url("http://localhost:8000")

        assert result["valid"] is True

    def test_ip_address_url(self):
        """Test IP address URLs are valid."""
        result = validate_url("http://192.168.1.1")

        assert result["valid"] is True

    def test_subdomain_url(self):
        """Test URLs with subdomains are valid."""
        result = validate_url("https://api.subdomain.example.com")

        assert result["valid"] is True

    def test_empty_string(self):
        """Test empty string is invalid."""
        result = validate_url("")

        assert result["valid"] is False
        assert "reason" in result

    def test_just_text(self):
        """Test plain text is invalid."""
        result = validate_url("not a url at all")

        assert result["valid"] is False
        assert "reason" in result


class TestNetworkToolsIntegration:
    """Integration tests for network tools."""

    @pytest.mark.asyncio
    async def test_validate_then_check_port(self):
        """Test validating URL then checking if its port is open."""
        url = "http://example.com:80"

        # First validate the URL
        validation_result = validate_url(url)
        assert validation_result["valid"] is True

        # Then check if port is open (mocked)
        with patch('asyncio.open_connection', new_callable=AsyncMock) as mock_conn:
            mock_conn.return_value = (None, None)

            port_result = await is_port_open("example.com", 80)
            assert port_result["open"] is True

    def test_multiple_url_validations(self):
        """Test validating multiple URLs in sequence."""
        urls = [
            "https://google.com",
            "http://localhost:3000",
            "ftp://files.example.com",
            "not a url",
            "https://api.example.com/v1/users"
        ]

        results = [validate_url(url) for url in urls]

        # First three should be valid
        assert results[0]["valid"] is True
        assert results[1]["valid"] is True
        assert results[2]["valid"] is True

        # Fourth should be invalid
        assert results[3]["valid"] is False

        # Fifth should be valid
        assert results[4]["valid"] is True