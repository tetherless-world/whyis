"""
Test CORS (Cross-Origin Resource Sharing) headers.

Verifies that CORS headers are properly set for API endpoints.
"""

import pytest


def test_cors_headers_on_root(client):
    """Test that CORS headers are present on root endpoint."""
    response = client.get('/')
    
    # Check for CORS headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert response.headers['Access-Control-Allow-Origin'] == '*'


def test_cors_preflight_request(client):
    """Test CORS preflight (OPTIONS) request with detailed header validation."""
    response = client.options(
        '/sparql',
        headers={
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
    )
    
    # Check CORS preflight response headers
    assert 'Access-Control-Allow-Origin' in response.headers
    assert 'Access-Control-Allow-Methods' in response.headers
    assert 'Access-Control-Allow-Headers' in response.headers
    
    # Validate allowed methods include expected values
    allowed_methods = response.headers.get('Access-Control-Allow-Methods', '')
    expected_methods = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    for method in expected_methods:
        assert method in allowed_methods, f"Expected method {method} not in allowed methods"
    
    # Validate allowed headers include expected values
    allowed_headers = response.headers.get('Access-Control-Allow-Headers', '').lower()
    expected_headers = ['content-type', 'authorization', 'accept']
    for header in expected_headers:
        assert header in allowed_headers, f"Expected header {header} not in allowed headers"


def test_cors_headers_on_sparql_endpoint(client):
    """Test that CORS headers are present on SPARQL endpoint."""
    response = client.get('/sparql')
    
    # Check for CORS headers
    assert 'Access-Control-Allow-Origin' in response.headers


def test_cors_headers_on_api_endpoint(client):
    """Test that CORS headers are present on API endpoints."""
    # Test with the nanopub list endpoint
    response = client.get('/pub/')
    
    # Check for CORS headers
    assert 'Access-Control-Allow-Origin' in response.headers


def test_cors_max_age_header(client):
    """Test that CORS max age header is set correctly."""
    response = client.options(
        '/sparql',
        headers={
            'Origin': 'http://example.com',
            'Access-Control-Request-Method': 'GET'
        }
    )
    
    # Check for max age header
    assert 'Access-Control-Max-Age' in response.headers
    # Verify it's set to 3600 (1 hour)
    assert response.headers['Access-Control-Max-Age'] == '3600'
