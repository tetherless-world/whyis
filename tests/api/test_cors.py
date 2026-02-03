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
    """Test CORS preflight (OPTIONS) request."""
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
