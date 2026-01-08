"""
Unit tests for NeptuneBoto3Store connector-level methods (_connector_query, _connector_update).

These tests specifically verify that the low-level connector methods work correctly,
including proper use of response_mime_types() and other inherited methods.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Skip all tests if dependencies not available
boto3 = pytest.importorskip("boto3")
pytest.importorskip("botocore")

from whyis.plugins.neptune.neptune_boto3_store import NeptuneBoto3Store


class TestNeptuneBoto3ConnectorQuery:
    """Test the _connector_query() method."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_connector_query_uses_response_mime_types(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _connector_query properly calls response_mime_types()."""
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
        mock_response.headers = {'Content-Type': 'application/sparql-results+json'}
        mock_response.content = b'{"head": {"vars": []}, "results": {"bindings": []}}'
        
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
        
        # Verify response_mime_types method exists and works
        mime_types = store.response_mime_types()
        assert mime_types is not None
        assert isinstance(mime_types, str)
        
        # Execute query through _connector_query
        query_string = "SELECT * WHERE { ?s ?p ?o }"
        result = store._connector_query(query_string)
        
        # Verify the request was made with Accept header containing MIME types
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        assert 'Accept' in call_args[1]['headers']
        # The Accept header should contain valid MIME types
        accept_header = call_args[1]['headers']['Accept']
        assert len(accept_header) > 0
        assert 'sparql-results' in accept_header or 'xml' in accept_header or 'json' in accept_header
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_connector_query_with_default_graph(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _connector_query handles default_graph parameter."""
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
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False
        )
        
        # Execute query with default_graph
        query_string = "SELECT * WHERE { ?s ?p ?o }"
        default_graph = "http://example.org/graph"
        result = store._connector_query(query_string, default_graph=default_graph)
        
        # Verify the request includes the default-graph-uri parameter
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        url = call_args[1]['url']
        assert 'default-graph-uri=' in url or 'query=' in url  # Depends on method
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_connector_query_error_reporting(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _connector_query provides good error messages on failure."""
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
        
        # Setup requests mock to return error
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 400
        mock_response.text = 'Bad Request: Invalid SPARQL syntax'
        
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
        
        # Execute query that will fail
        query_string = "INVALID QUERY"
        
        with pytest.raises(IOError) as exc_info:
            store._connector_query(query_string)
        
        # Verify error message contains useful information
        error_msg = str(exc_info.value)
        assert 'Neptune SPARQL query failed' in error_msg
        assert '400' in error_msg
        assert 'Bad Request' in error_msg


class TestNeptuneBoto3ConnectorUpdate:
    """Test the _connector_update() method."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_connector_update_uses_response_mime_types(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _connector_update properly calls response_mime_types()."""
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
        
        # Verify response_mime_types method exists and works
        mime_types = store.response_mime_types()
        assert mime_types is not None
        
        # Execute update through _connector_update
        update_string = "INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }"
        store._connector_update(update_string)
        
        # Verify the request was made with Accept header
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        assert 'Accept' in call_args[1]['headers']
        assert 'Content-Type' in call_args[1]['headers']
        assert 'application/sparql-update' in call_args[1]['headers']['Content-Type']


class TestNeptuneBoto3StoreQueryShortcuts:
    """Test the _query() shortcut method."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_query_shortcut_increments_counter(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _query() properly increments the query counter."""
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
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False
        )
        
        # Check initial counter
        initial_count = store._queries
        
        # Execute query through _query shortcut
        query_string = "SELECT * WHERE { ?s ?p ?o }"
        store._query(query_string)
        
        # Verify counter was incremented
        assert store._queries == initial_count + 1
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_update_shortcut_increments_counter(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _update() properly increments the update counter."""
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
        
        # Check initial counter
        initial_count = store._updates
        
        # Execute update through _update shortcut
        update_string = "INSERT DATA { <http://example.org/s> <http://example.org/p> <http://example.org/o> }"
        store._update(update_string)
        
        # Verify counter was incremented
        assert store._updates == initial_count + 1
