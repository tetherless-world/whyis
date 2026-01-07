"""
Unit tests for NeptuneBoto3Store class.

Tests the new boto3-based Neptune SPARQL store implementation that provides
AWS IAM authentication using boto3's credential management and instance metadata.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock
from io import BytesIO

# Skip all tests if dependencies not available
boto3 = pytest.importorskip("boto3")
pytest.importorskip("botocore")

from whyis.plugins.neptune.neptune_boto3_store import NeptuneBoto3Store


class TestNeptuneBoto3StoreInit:
    """Test NeptuneBoto3Store initialization."""
    
    def test_store_requires_region_name(self):
        """Test that store requires region_name parameter."""
        with pytest.raises(ValueError, match="region_name is required"):
            NeptuneBoto3Store(
                query_endpoint='https://neptune.example.com/sparql',
                update_endpoint='https://neptune.example.com/sparql'
            )
    
    @patch('boto3.Session')
    def test_store_creates_boto3_session(self, mock_session_class):
        """Test that store creates a boto3 session if not provided."""
        mock_session = Mock()
        mock_credentials = Mock()
        mock_credentials.get_frozen_credentials.return_value = Mock(
            access_key='test_key',
            secret_key='test_secret',
            token=None
        )
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Verify boto3.Session was called
        mock_session_class.assert_called_once()
        assert store.region_name == 'us-east-1'
        assert store.service_name == 'neptune-db'
    
    @patch('boto3.Session')
    def test_store_uses_provided_boto3_session(self, mock_session_class):
        """Test that store uses provided boto3 session."""
        mock_session = Mock()
        mock_credentials = Mock()
        mock_credentials.get_frozen_credentials.return_value = Mock(
            access_key='test_key',
            secret_key='test_secret',
            token=None
        )
        mock_session.get_credentials.return_value = mock_credentials
        
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-west-2',
            boto3_session=mock_session
        )
        
        # Verify provided session was used
        mock_session_class.assert_not_called()
        assert store.boto3_session is mock_session
    
    @patch('boto3.Session')
    def test_store_accepts_custom_service_name(self, mock_session_class):
        """Test that store accepts custom service name."""
        mock_session = Mock()
        mock_credentials = Mock()
        mock_credentials.get_frozen_credentials.return_value = Mock(
            access_key='test_key',
            secret_key='test_secret',
            token=None
        )
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='eu-west-1',
            service_name='custom-service'
        )
        
        assert store.service_name == 'custom-service'
    
    @patch('boto3.Session')
    def test_store_raises_error_without_credentials(self, mock_session_class):
        """Test that store raises error when no credentials are available and instance metadata disabled."""
        mock_session = Mock()
        mock_session.get_credentials.return_value = None
        mock_session_class.return_value = mock_session
        
        with pytest.raises(ValueError, match="No AWS credentials found"):
            NeptuneBoto3Store(
                query_endpoint='https://neptune.example.com/sparql',
                update_endpoint='https://neptune.example.com/sparql',
                region_name='us-east-1',
                use_instance_metadata=False  # Disable instance metadata to ensure error is raised
            )
    
    @patch('whyis.plugins.neptune.neptune_boto3_store.InstanceMetadataFetcher')
    @patch('whyis.plugins.neptune.neptune_boto3_store.InstanceMetadataProvider')
    @patch('boto3.Session')
    def test_store_initializes_instance_metadata_provider(self, mock_session_class, 
                                                          mock_provider_class, mock_fetcher_class):
        """Test that store initializes instance metadata provider by default."""
        mock_session = Mock()
        mock_credentials = Mock()
        mock_credentials.get_frozen_credentials.return_value = Mock(
            access_key='test_key',
            secret_key='test_secret',
            token=None
        )
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        mock_provider = Mock()
        mock_provider_class.return_value = mock_provider
        
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=True
        )
        
        # Verify instance metadata components were created
        mock_fetcher_class.assert_called_once()
        mock_provider_class.assert_called_once_with(iam_role_fetcher=mock_fetcher)
        assert store._instance_metadata_provider is mock_provider
    
    @patch('boto3.Session')
    def test_store_skips_instance_metadata_when_disabled(self, mock_session_class):
        """Test that store skips instance metadata provider when disabled."""
        mock_session = Mock()
        mock_credentials = Mock()
        mock_credentials.get_frozen_credentials.return_value = Mock(
            access_key='test_key',
            secret_key='test_secret',
            token=None
        )
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False
        )
        
        # Verify instance metadata provider was not created
        assert store._instance_metadata_provider is None


class TestNeptuneBoto3StoreInstanceMetadata:
    """Test dynamic credential retrieval from instance metadata."""
    
    @patch('whyis.plugins.neptune.neptune_boto3_store.InstanceMetadataFetcher')
    @patch('whyis.plugins.neptune.neptune_boto3_store.InstanceMetadataProvider')
    @patch('boto3.Session')
    def test_get_credentials_from_instance_metadata(self, mock_session_class,
                                                     mock_provider_class, mock_fetcher_class):
        """Test that _get_credentials retrieves from instance metadata provider."""
        # Setup mocks
        mock_session = Mock()
        mock_session_credentials = Mock()
        mock_session_credentials.get_frozen_credentials.return_value = Mock(
            access_key='session_key',
            secret_key='session_secret',
            token=None
        )
        mock_session.get_credentials.return_value = mock_session_credentials
        mock_session_class.return_value = mock_session
        
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock instance metadata credentials
        mock_instance_creds = Mock()
        mock_frozen_instance_creds = Mock()
        mock_frozen_instance_creds.access_key = 'instance_key'
        mock_frozen_instance_creds.secret_key = 'instance_secret'
        mock_frozen_instance_creds.token = 'instance_token'
        mock_instance_creds.get_frozen_credentials.return_value = mock_frozen_instance_creds
        
        mock_provider = Mock()
        mock_provider.load.return_value = mock_instance_creds
        mock_provider_class.return_value = mock_provider
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=True
        )
        
        # Get credentials
        frozen_creds = store._get_credentials()
        
        # Verify instance metadata provider was called
        mock_provider.load.assert_called_once()
        
        # Verify we got instance metadata credentials (not session credentials)
        assert frozen_creds.access_key == 'instance_key'
        assert frozen_creds.secret_key == 'instance_secret'
        assert frozen_creds.token == 'instance_token'
    
    @patch('whyis.plugins.neptune.neptune_boto3_store.InstanceMetadataFetcher')
    @patch('whyis.plugins.neptune.neptune_boto3_store.InstanceMetadataProvider')
    @patch('boto3.Session')
    def test_get_credentials_falls_back_to_session(self, mock_session_class,
                                                    mock_provider_class, mock_fetcher_class):
        """Test that _get_credentials falls back to session when instance metadata fails."""
        # Setup mocks
        mock_session = Mock()
        mock_session_credentials = Mock()
        mock_frozen_session_creds = Mock()
        mock_frozen_session_creds.access_key = 'session_key'
        mock_frozen_session_creds.secret_key = 'session_secret'
        mock_frozen_session_creds.token = None
        mock_session_credentials.get_frozen_credentials.return_value = mock_frozen_session_creds
        mock_session.get_credentials.return_value = mock_session_credentials
        mock_session_class.return_value = mock_session
        
        mock_fetcher = Mock()
        mock_fetcher_class.return_value = mock_fetcher
        
        # Mock instance metadata provider to return None (not available)
        mock_provider = Mock()
        mock_provider.load.return_value = None
        mock_provider_class.return_value = mock_provider
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=True
        )
        
        # Get credentials
        frozen_creds = store._get_credentials()
        
        # Verify we got session credentials as fallback
        assert frozen_creds.access_key == 'session_key'
        assert frozen_creds.secret_key == 'session_secret'
    
    @patch('boto3.Session')
    def test_get_credentials_without_instance_metadata(self, mock_session_class):
        """Test that _get_credentials uses session when instance metadata is disabled."""
        mock_session = Mock()
        mock_session_credentials = Mock()
        mock_frozen_creds = Mock()
        mock_frozen_creds.access_key = 'session_key'
        mock_frozen_creds.secret_key = 'session_secret'
        mock_frozen_creds.token = None
        mock_session_credentials.get_frozen_credentials.return_value = mock_frozen_creds
        mock_session.get_credentials.return_value = mock_session_credentials
        mock_session_class.return_value = mock_session
        
        # Create store with instance metadata disabled
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            use_instance_metadata=False
        )
        
        # Get credentials
        frozen_creds = store._get_credentials()
        
        # Verify we got session credentials
        assert frozen_creds.access_key == 'session_key'
        assert frozen_creds.secret_key == 'session_secret'


class TestNeptuneBoto3StoreRequestSigning:
    """Test request signing with boto3."""
    
    @patch('boto3.Session')
    def test_sign_request_adds_signature_headers(self, mock_session_class):
        """Test that _sign_request adds AWS signature headers."""
        # Setup mock session and credentials
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_session = Mock()
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Sign a request
        headers = {'Content-Type': 'application/sparql-query'}
        signed_headers = store._sign_request(
            method='POST',
            url='https://neptune.example.com/sparql',
            headers=headers,
            body='SELECT * WHERE { ?s ?p ?o }'
        )
        
        # Verify signature headers are present
        assert 'Authorization' in signed_headers
        assert signed_headers['Content-Type'] == 'application/sparql-query'
        assert 'AWS4-HMAC-SHA256' in signed_headers['Authorization']
    
    @patch('boto3.Session')
    def test_sign_request_handles_query_parameters(self, mock_session_class):
        """Test that _sign_request properly handles URLs with query parameters."""
        # Setup mock session and credentials
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_session = Mock()
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Sign a request with query parameters
        url_with_params = 'https://neptune.example.com/sparql?query=SELECT%20*'
        signed_headers = store._sign_request(
            method='GET',
            url=url_with_params,
            headers={}
        )
        
        # Verify signature was added
        assert 'Authorization' in signed_headers
    
    @patch('boto3.Session')
    def test_sign_request_with_session_token(self, mock_session_class):
        """Test that _sign_request works with temporary credentials (session token)."""
        # Setup mock session with temporary credentials
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'temp_key'
        frozen_creds.secret_key = 'temp_secret'
        frozen_creds.token = 'session_token'
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_session = Mock()
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Sign a request
        signed_headers = store._sign_request(
            method='POST',
            url='https://neptune.example.com/sparql',
            headers={'Content-Type': 'application/sparql-query'}
        )
        
        # Verify signature headers are present (including session token)
        assert 'Authorization' in signed_headers
        assert 'X-Amz-Security-Token' in signed_headers or 'x-amz-security-token' in signed_headers


class TestNeptuneBoto3StoreHTTPRequests:
    """Test HTTP request methods."""
    
    @patch('requests.Session')
    @patch('boto3.Session')
    def test_request_method_signs_and_sends(self, mock_boto_session_class, mock_requests_session_class):
        """Test that _request method signs request and sends it."""
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
        mock_response.status_code = 200
        mock_response.text = 'OK'
        
        mock_requests_session = Mock()
        mock_requests_session.request.return_value = mock_response
        mock_requests_session_class.return_value = mock_requests_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Make a request
        response = store._request(
            method='POST',
            url='https://neptune.example.com/sparql',
            headers={'Content-Type': 'application/sparql-query'},
            body='SELECT * WHERE { ?s ?p ?o }'
        )
        
        # Verify request was made
        assert mock_requests_session.request.called
        call_args = mock_requests_session.request.call_args
        
        # Check that method and URL are correct
        assert call_args[1]['method'] == 'POST'
        assert call_args[1]['url'] == 'https://neptune.example.com/sparql'
        
        # Check that headers include authorization
        assert 'Authorization' in call_args[1]['headers']
        
        # Check response
        assert response.status_code == 200


class TestNeptuneBoto3StoreIntegration:
    """Test integration with RDFlib."""
    
    @patch('boto3.Session')
    def test_store_can_be_used_with_conjunctive_graph(self, mock_session_class):
        """Test that store can be used with RDFlib's ConjunctiveGraph."""
        from rdflib.graph import ConjunctiveGraph
        
        # Setup mock session
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_session = Mock()
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Create graph with the store
        graph = ConjunctiveGraph(store)
        
        # Verify graph was created
        assert isinstance(graph, ConjunctiveGraph)
        assert graph.store is store
    
    @patch('boto3.Session')
    def test_store_inherits_from_whyis_sparql_update_store(self, mock_session_class):
        """Test that store properly inherits from WhyisSPARQLUpdateStore."""
        from whyis.database.whyis_sparql_update_store import WhyisSPARQLUpdateStore
        
        # Setup mock session
        mock_credentials = Mock()
        frozen_creds = Mock()
        frozen_creds.access_key = 'test_key'
        frozen_creds.secret_key = 'test_secret'
        frozen_creds.token = None
        mock_credentials.get_frozen_credentials.return_value = frozen_creds
        
        mock_session = Mock()
        mock_session.get_credentials.return_value = mock_credentials
        mock_session_class.return_value = mock_session
        
        # Create store
        store = NeptuneBoto3Store(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Verify inheritance
        assert isinstance(store, WhyisSPARQLUpdateStore)
        assert hasattr(store, '_inject_prefixes')  # Method from WhyisSPARQLUpdateStore


class TestNeptuneBoto3StoreMissingBoto3:
    """Test behavior when boto3 is not installed."""
    
    def test_import_error_when_boto3_not_available(self):
        """Test that appropriate error is raised when boto3 is not available."""
        # This test is mainly for documentation - in practice, pytest.importorskip
        # will skip these tests if boto3 is not available
        
        # We can't actually test this without uninstalling boto3,
        # but we document the expected behavior
        pass
