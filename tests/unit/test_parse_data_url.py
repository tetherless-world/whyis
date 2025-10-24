"""
Unit tests for whyis.dataurl.parse_data_url module.

Tests the parse_data_url function for parsing data URLs.
"""

import pytest
import binascii
from whyis.dataurl.parse_data_url import parse_data_url


class TestParseDataUrl:
    """Test the parse_data_url function."""
    
    def test_parse_data_url_exists(self):
        """Test that parse_data_url function exists."""
        assert parse_data_url is not None
        assert callable(parse_data_url)
    
    def test_parse_simple_text_data_url(self):
        """Test parsing a simple text data URL."""
        url = "data:text/plain,Hello%20World"
        data, content_type = parse_data_url(url)
        assert data == b"Hello World"
        assert content_type == "text/plain"
    
    def test_parse_base64_data_url(self):
        """Test parsing a base64-encoded data URL."""
        # "Hello World" in base64 is "SGVsbG8gV29ybGQ="
        url = "data:text/plain;base64,SGVsbG8gV29ybGQ="
        data, content_type = parse_data_url(url)
        assert data == b"Hello World"
        assert content_type == "text/plain"
    
    def test_parse_data_url_with_charset(self):
        """Test parsing data URL with charset."""
        url = "data:text/plain;charset=utf-8,Hello"
        data, content_type = parse_data_url(url)
        assert data == b"Hello"
        assert content_type == "text/plain;charset=utf-8"
    
    def test_parse_empty_content_type(self):
        """Test parsing data URL with empty content type."""
        url = "data:,Hello"
        data, content_type = parse_data_url(url)
        assert data == b"Hello"
        assert content_type is None
    
    def test_parse_base64_with_empty_content_type(self):
        """Test parsing base64 data URL with empty content type."""
        url = "data:;base64,SGVsbG8="
        data, content_type = parse_data_url(url)
        assert data == b"Hello"
        assert content_type is None
    
    def test_parse_url_encoded_data(self):
        """Test parsing URL-encoded data."""
        url = "data:text/plain,Hello%2C%20World%21"
        data, content_type = parse_data_url(url)
        assert data == b"Hello, World!"
        assert content_type == "text/plain"
    
    def test_parse_json_data_url(self):
        """Test parsing JSON data URL."""
        url = "data:application/json,%7B%22key%22%3A%22value%22%7D"
        data, content_type = parse_data_url(url)
        assert data == b'{"key":"value"}'
        assert content_type == "application/json"
    
    def test_parse_base64_json_data_url(self):
        """Test parsing base64-encoded JSON data URL."""
        # '{"test":true}' in base64 is 'eyJ0ZXN0Ijp0cnVlfQ=='
        url = "data:application/json;base64,eyJ0ZXN0Ijp0cnVlfQ=="
        data, content_type = parse_data_url(url)
        assert data == b'{"test":true}'
        assert content_type == "application/json"
    
    def test_parse_image_data_url(self):
        """Test parsing image data URL (base64)."""
        # Simple 1x1 pixel GIF in base64
        gif_base64 = "R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=="
        url = f"data:image/gif;base64,{gif_base64}"
        data, content_type = parse_data_url(url)
        assert len(data) > 0
        assert content_type == "image/gif"
    
    def test_parse_data_url_with_special_characters(self):
        """Test parsing data URL with special characters."""
        url = "data:text/plain,Test%20%26%20Special%20%3C%3E"
        data, content_type = parse_data_url(url)
        assert data == b"Test & Special <>"
        assert content_type == "text/plain"
    
    def test_invalid_scheme_raises_assertion(self):
        """Test that non-data scheme raises AssertionError."""
        url = "http://example.com/test"
        with pytest.raises(AssertionError, match="unsupported scheme"):
            parse_data_url(url)
    
    def test_parse_data_url_with_padding(self):
        """Test parsing base64 data URL with padding."""
        # Test with proper padding
        url = "data:text/plain;base64,VGVzdA=="
        data, content_type = parse_data_url(url)
        assert data == b"Test"
        assert content_type == "text/plain"
    
    def test_parse_data_url_returns_tuple(self):
        """Test that parse_data_url returns a tuple."""
        url = "data:text/plain,test"
        result = parse_data_url(url)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_parse_data_url_returns_bytes(self):
        """Test that parse_data_url returns bytes as first element."""
        url = "data:text/plain,test"
        data, content_type = parse_data_url(url)
        assert isinstance(data, bytes)
    
    def test_parse_data_url_content_type_is_string_or_none(self):
        """Test that content type is string or None."""
        url = "data:text/plain,test"
        data, content_type = parse_data_url(url)
        assert content_type is None or isinstance(content_type, str)
    
    def test_parse_csv_data_url(self):
        """Test parsing CSV data URL."""
        csv_data = "name,age%0AJohn,30"
        url = f"data:text/csv,{csv_data}"
        data, content_type = parse_data_url(url)
        assert b"name,age" in data
        assert content_type == "text/csv"
    
    def test_parse_html_data_url(self):
        """Test parsing HTML data URL."""
        html = "%3Chtml%3E%3Cbody%3EHello%3C%2Fbody%3E%3C%2Fhtml%3E"
        url = f"data:text/html,{html}"
        data, content_type = parse_data_url(url)
        assert b"<html>" in data
        assert content_type == "text/html"
    
    def test_parse_base64_with_multiple_params(self):
        """Test parsing base64 URL with multiple parameters."""
        url = "data:text/plain;charset=utf-8;base64,SGVsbG8="
        data, content_type = parse_data_url(url)
        assert data == b"Hello"
        assert content_type == "text/plain;charset=utf-8"
