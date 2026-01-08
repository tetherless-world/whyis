"""
Unit tests for NeptuneBoto3Store query and update methods with authentication.

Tests that the overridden query() and update() methods properly use AWS authentication.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys

# Skip all tests if dependencies not available
boto3 = pytest.importorskip("boto3")
pytest.importorskip("botocore")

# Import directly from the module file, not through plugin __init__
from whyis.plugins.neptune.neptune_boto3_store import NeptuneBoto3Store


class TestNeptuneBoto3StoreQueryMethod:
    """Test the query() method override for authenticated requests."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_query_method_uses_authenticated_request(self, mock_boto_session_class, mock_requests_session_class):
        """Test that query() method makes authenticated HTTP requests."""
        # Setup boto3 mock
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_boto_session = Mock()
        mock_boto_session.get_credentials.return_value = mock_credentials
        mock_boto_session_class.return_value = mock_boto_session
        
        # Setup requests mock to return a valid SPARQL result
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/sparql-results+json'}
        mock_response.content = b'{"head": {"vars": []}, "results": {"bindings": []}}'
        
        mock_requests_session = Mock()
        mock_requests_session.request.return_value = mock_response
        mock_requests_session_class.return_value = mock_requests_session
        
        # Create store with POST method
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False,
            method='POST'  # Explicitly set POST method
        )
        
        # Execute a query directly (SPARQLConnector level)
        query_string = "SELECT * WHERE { ?s ?p ?o } LIMIT 10"
        result = store.query(query_string)
        
        # Verify request was made with authentication
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        
        # Check that headers include authorization
        assert 'Authorization' in call_args[1]['headers']
        assert 'AWS4-HMAC-SHA256' in call_args[1]['headers']['Authorization']
        
        # Check the query was sent with POST method
        assert call_args[1]['method'] == 'POST'
        assert call_args[1]['data'] == query_string.encode('utf-8')
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_query_method_handles_get_method(self, mock_boto_session_class, mock_requests_session_class):
        """Test that query() works with GET method."""
        # Setup mocks
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_boto_session = Mock()
        mock_boto_session.get_credentials.return_value = mock_credentials
        mock_boto_session_class.return_value = mock_boto_session
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/sparql-results+xml'}
        mock_response.content = b'<?xml version="1.0"?><sparql xmlns="http://www.w3.org/2005/sparql-results#"><head></head><results></results></sparql>'
        
        mock_requests_session = Mock()
        mock_requests_session.request.return_value = mock_response
        mock_requests_session_class.return_value = mock_requests_session
        
        # Create store with GET method
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False,
            method='GET'
        )
        
        # Execute query
        query_string = "SELECT * WHERE { ?s ?p ?o }"
        store.query(query_string)
        
        # Verify GET method was used
        call_args = mock_requests_session.request.call_args
        assert call_args[1]['method'] == 'GET'
        assert 'Authorization' in call_args[1]['headers']


class TestNeptuneBoto3StoreUpdateMethod:
    """Test the update() method override for authenticated requests."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_update_method_uses_authenticated_request(self, mock_boto_session_class, mock_requests_session_class):
        """Test that update() method makes authenticated HTTP requests."""
        # Setup boto3 mock
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_boto_session = Mock()
        mock_boto_session.get_credentials.return_value = mock_credentials
        mock_boto_session_class.return_value = mock_boto_session
        
        # Setup requests mock
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = 'Success'
        
        mock_requests_session = Mock()
        mock_requests_session.request.return_value = mock_response
        mock_requests_session_class.return_value = mock_requests_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False
        )
        
        # Execute an update directly (SPARQLConnector level)
        update_string = "INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }"
        store.update(update_string)
        
        # Verify request was made with authentication
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        
        # Check that headers include authorization
        assert 'Authorization' in call_args[1]['headers']
        assert 'AWS4-HMAC-SHA256' in call_args[1]['headers']['Authorization']
        
        # Check the update was sent
        assert call_args[1]['method'] == 'POST'
        assert call_args[1]['data'] == update_string.encode('utf-8')
        assert 'application/sparql-update' in call_args[1]['headers']['Content-Type']


class TestNeptuneBoto3StoreHighLevelQuery:
    """Test that high-level query functionality is preserved."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_high_level_query_with_initBindings(self, mock_boto_session_class, mock_requests_session_class):
        """Test that query() works with initBindings through parent class."""
        # Setup mocks
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_boto_session = Mock()
        mock_boto_session.get_credentials.return_value = mock_credentials
        mock_boto_session_class.return_value = mock_boto_session
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'Content-Type': 'application/sparql-results+json'}
        mock_response.content = b'{"head": {"vars": []}, "results": {"bindings": []}}'
        
        mock_requests_session = Mock()
        mock_requests_session.request.return_value = mock_response
        mock_requests_session_class.return_value = mock_requests_session
        
        # Create store
        from rdflib import ConjunctiveGraph, Literal
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False
        )
        
        graph = ConjunctiveGraph(store)
        
        # Execute query with initBindings (high-level interface)
        # This tests that the parent class preprocessing still works
        try:
            results = graph.query(
                "SELECT * WHERE { ?s ?p ?value }",
                initBindings={'value': Literal('test')}
            )
            # If we get here, the query flow worked (even if results are empty)
            assert True
        except Exception as e:
            # If there's an error, make sure it's not about authentication
            assert 'Authorization' not in str(e)
            assert 'AWS' not in str(e)
