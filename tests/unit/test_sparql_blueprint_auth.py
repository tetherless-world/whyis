"""
Unit tests for SPARQL blueprint authentication.

Tests that the SPARQL blueprint properly uses store authentication methods.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

# Skip all tests if dependencies not available
boto3 = pytest.importorskip("boto3")
pytest.importorskip("botocore")

from whyis.plugins.neptune.neptune_boto3_store import NeptuneBoto3Store
from whyis.database.whyis_sparql_update_store import WhyisSPARQLUpdateStore


class TestNeptuneBoto3StoreRawRequest:
    """Test the raw_sparql_request method for NeptuneBoto3Store."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_raw_sparql_request_get(self, mock_boto_session_class, mock_requests_session_class):
        """Test raw_sparql_request with GET method."""
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
        mock_response.headers = {'content-type': 'application/sparql-results+json'}
        mock_response.content = b'{"results": {}}'
        mock_response.iter_content = Mock(return_value=[b'{"results": {}}'])
        
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
        
        # Make raw request
        params = {'query': 'SELECT * WHERE { ?s ?p ?o }'}
        headers = {'Accept': 'application/sparql-results+json'}
        
        response = store.raw_sparql_request(
            method='GET',
            params=params,
            headers=headers
        )
        
        # Verify request was made with authentication
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        
        # Check that authorization header was added
        assert 'Authorization' in call_args[1]['headers']
        assert 'AWS4-HMAC-SHA256' in call_args[1]['headers']['Authorization']
        
        # Check response
        assert response.ok
        assert response.status_code == 200
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_raw_sparql_request_post(self, mock_boto_session_class, mock_requests_session_class):
        """Test raw_sparql_request with POST method."""
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
        mock_response.headers = {'content-type': 'application/sparql-results+xml'}
        mock_response.content = b'<results/>'
        mock_response.iter_content = Mock(return_value=[b'<results/>'])
        
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
        
        # Make raw POST request
        data = b'query=SELECT * WHERE { ?s ?p ?o }'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        
        response = store.raw_sparql_request(
            method='POST',
            data=data,
            headers=headers
        )
        
        # Verify request was made with authentication
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        
        # Check that authorization header was added
        assert 'Authorization' in call_args[1]['headers']
        
        # Check response
        assert response.ok


class TestWhyisSPARQLUpdateStoreRawRequest:
    """Test the raw_sparql_request method for WhyisSPARQLUpdateStore."""
    
    @patch('requests.request')
    def test_raw_sparql_request_with_basic_auth(self, mock_request):
        """Test raw_sparql_request with HTTP Basic Auth."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/sparql-results+json'}
        mock_response.content = b'{"results": {}}'
        mock_response.iter_content = Mock(return_value=[b'{"results": {}}'])
        mock_request.return_value = mock_response
        
        # Create store with auth
        store = WhyisSPARQLUpdateStore(
            query_endpoint='http://localhost:3030/test/sparql',
            update_endpoint='http://localhost:3030/test/sparql',
            auth=('user', 'pass')
        )
        store.auth = ('user', 'pass')
        
        # Make raw request
        params = {'query': 'SELECT * WHERE { ?s ?p ?o }'}
        headers = {'Accept': 'application/sparql-results+json'}
        
        response = store.raw_sparql_request(
            method='GET',
            params=params,
            headers=headers
        )
        
        # Verify request was made with auth
        assert mock_request.called
        call_args = mock_request.call_args
        
        # Check that auth was passed
        assert 'auth' in call_args[1]
        assert call_args[1]['auth'] == ('user', 'pass')
        
        # Check response
        assert response.ok
    
    @patch('requests.request')
    def test_raw_sparql_request_without_auth(self, mock_request):
        """Test raw_sparql_request without authentication."""
        # Setup mock response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'application/sparql-results+json'}
        mock_response.content = b'{"results": {}}'
        mock_response.iter_content = Mock(return_value=[b'{"results": {}}'])
        mock_request.return_value = mock_response
        
        # Create store without auth
        store = WhyisSPARQLUpdateStore(
            query_endpoint='http://localhost:3030/test/sparql',
            update_endpoint='http://localhost:3030/test/sparql'
        )
        store.auth = None
        
        # Make raw request
        params = {'query': 'SELECT * WHERE { ?s ?p ?o }'}
        
        response = store.raw_sparql_request(
            method='GET',
            params=params
        )
        
        # Verify request was made without auth
        assert mock_request.called
        call_args = mock_request.call_args
        
        # Check that auth was not passed (or is None)
        assert 'auth' not in call_args[1] or call_args[1].get('auth') is None
        
        # Check response
        assert response.ok
