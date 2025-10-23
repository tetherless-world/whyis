"""
Unit tests for whyis.dataurl.data_response module.

Tests the DataResponse class for handling data URLs as HTTP responses.
"""

import pytest

# Skip all tests if dependencies not available
pytest.importorskip("flask_security")

from whyis.dataurl.data_response import DataResponse


class TestDataResponse:
    """Test the DataResponse class."""
    
    def test_data_response_with_text(self):
        """Test DataResponse with plain text data URL."""
        url = "data:text/plain,Hello%20World"
        response = DataResponse(url)
        
        assert response.read() == b"Hello World"
        assert response.mediatype == "text/plain"
    
    def test_data_response_with_base64(self):
        """Test DataResponse with base64 data URL."""
        url = "data:text/plain;base64,SGVsbG8="
        response = DataResponse(url)
        
        assert response.read() == b"Hello"
        assert response.mediatype == "text/plain"
    
    def test_data_response_url_property(self):
        """Test that DataResponse stores the URL."""
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        assert response.url == url
    
    def test_data_response_geturl_method(self):
        """Test DataResponse geturl method."""
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        assert response.geturl() == url
    
    def test_data_response_length(self):
        """Test that DataResponse calculates correct length."""
        url = "data:text/plain,Hello"
        response = DataResponse(url)
        
        assert response.length == 5
    
    def test_data_response_headers(self):
        """Test that DataResponse has headers."""
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        assert response.headers is not None
        assert response.msg is not None
    
    def test_data_response_content_type_header(self):
        """Test that Content-Type header is set correctly."""
        url = "data:text/html,<html></html>"
        response = DataResponse(url)
        
        content_type = response.getheader("Content-Type")
        assert content_type == "text/html"
    
    def test_data_response_getheader_not_found(self):
        """Test getheader with non-existent header."""
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        result = response.getheader("X-Custom-Header", "default")
        assert result == "default"
    
    def test_data_response_getheaders(self):
        """Test getheaders method."""
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        headers = response.getheaders()
        assert isinstance(headers, list)
    
    def test_data_response_info(self):
        """Test info method returns headers."""
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        info = response.info()
        assert info == response.headers
    
    def test_data_response_empty_content_type(self):
        """Test DataResponse with empty content type."""
        url = "data:,test"
        response = DataResponse(url)
        
        assert response.mediatype is None
        assert response.read() == b"test"
    
    def test_data_response_json_content(self):
        """Test DataResponse with JSON data."""
        url = "data:application/json,%7B%22key%22%3A%22value%22%7D"
        response = DataResponse(url)
        
        assert response.mediatype == "application/json"
        assert response.read() == b'{"key":"value"}'
    
    def test_data_response_is_bytesio(self):
        """Test that DataResponse is a BytesIO subclass."""
        import io
        url = "data:text/plain,test"
        response = DataResponse(url)
        
        assert isinstance(response, io.BytesIO)
    
    def test_data_response_seek_and_read(self):
        """Test that DataResponse supports seek and read operations."""
        url = "data:text/plain,Hello%20World"
        response = DataResponse(url)
        
        # Read first 5 bytes
        assert response.read(5) == b"Hello"
        
        # Seek back to start
        response.seek(0)
        
        # Read all
        assert response.read() == b"Hello World"
