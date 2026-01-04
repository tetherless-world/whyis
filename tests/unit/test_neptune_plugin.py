"""
Unit tests for Neptune SPARQL store with IAM authentication.

Tests the Neptune-specific store implementations that support AWS IAM authentication.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Skip all tests if dependencies not available
pytest.importorskip("flask_security")
pytest.importorskip("boto3")
pytest.importorskip("requests_aws4auth")

from rdflib import URIRef, Namespace, Literal
from rdflib.graph import ConjunctiveGraph
from whyis.plugins.neptune.neptune_sparql_store import (
    NeptuneSPARQLConnector,
    NeptuneSPARQLStore,
    NeptuneSPARQLUpdateStore
)
from whyis.database.database_utils import drivers, node_to_sparql


class TestNeptuneSPARQLConnector:
    """Test the NeptuneSPARQLConnector class."""
    
    def test_connector_initialization(self):
        """Test that connector initializes with AWS configuration."""
        connector = NeptuneSPARQLConnector(
            query_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            service_name='neptune-db'
        )
        
        assert connector.region_name == 'us-east-1'
        assert connector.service_name == 'neptune-db'
        assert connector._aws_auth is None  # Not created until first use
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_get_session_creates_auth(self, mock_session):
        """Test that _get_session creates AWS authentication."""
        # Mock credentials
        mock_creds = Mock()
        mock_creds.access_key = 'test_access_key'
        mock_creds.secret_key = 'test_secret_key'
        mock_creds.token = 'test_token'
        mock_session.return_value.get_credentials.return_value = mock_creds
        
        connector = NeptuneSPARQLConnector(
            query_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        session = connector._get_session()
        
        assert session is not None
        assert connector._aws_auth is not None
        mock_session.return_value.get_credentials.assert_called_once()
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    @patch('whyis.plugins.neptune.neptune_sparql_store.requests.Session')
    def test_query_with_auth(self, mock_requests_session, mock_boto_session):
        """Test that query method uses AWS authentication."""
        # Mock credentials
        mock_creds = Mock()
        mock_creds.access_key = 'test_key'
        mock_creds.secret_key = 'test_secret'
        mock_creds.token = None
        mock_boto_session.return_value.get_credentials.return_value = mock_creds
        
        # Mock response with proper SPARQL JSON structure
        mock_response = Mock()
        mock_response.content = b'{"head": {"vars": ["s", "p", "o"]}, "results": {"bindings": []}}'
        mock_response.headers = {'Content-Type': 'application/sparql-results+json'}
        mock_response.raise_for_status = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_requests_session.return_value = mock_session_instance
        
        connector = NeptuneSPARQLConnector(
            query_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1',
            method='POST'
        )
        
        # Execute query
        query = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 10"
        result = connector.query(query)
        
        # Verify auth was set up and request was made
        assert mock_session_instance.auth is not None
        mock_session_instance.post.assert_called_once()


class TestNeptuneSPARQLStore:
    """Test the NeptuneSPARQLStore class."""
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_store_initialization(self, mock_session):
        """Test that store initializes correctly."""
        store = NeptuneSPARQLStore(
            query_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        assert hasattr(store, '_connector')
        assert store._connector.region_name == 'us-east-1'
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_inject_prefixes(self, mock_session):
        """Test that _inject_prefixes works correctly."""
        store = NeptuneSPARQLStore(
            query_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        query = "SELECT ?s WHERE { ?s rdf:type ?o }"
        bindings = {'rdf': Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')}
        
        result = store._inject_prefixes(query, bindings)
        
        assert 'PREFIX rdf:' in result
        assert query in result


class TestNeptuneSPARQLUpdateStore:
    """Test the NeptuneSPARQLUpdateStore class."""
    
    def test_update_store_initialization(self):
        """Test that update store initializes correctly."""
        store = NeptuneSPARQLUpdateStore(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        assert store.region_name == 'us-east-1'
        assert hasattr(store, '_connector')
    
    def test_inject_prefixes(self):
        """Test that _inject_prefixes works correctly."""
        store = NeptuneSPARQLUpdateStore(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        query = "SELECT ?s WHERE { ?s rdf:type ?o }"
        bindings = {'rdf': Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')}
        
        result = store._inject_prefixes(query, bindings)
        
        assert 'PREFIX rdf:' in result
        assert query in result


class TestNeptuneDriver:
    """Test the Neptune driver registration and functionality."""
    
    def test_neptune_driver_can_be_registered(self):
        """Test that neptune driver can be registered by plugin."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        # Verify the function exists and is callable
        assert callable(neptune_driver)
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_neptune_driver_requires_region(self, mock_neptune_session):
        """Test that neptune driver requires region configuration."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql'
        }
        
        with pytest.raises(ValueError, match="requires '_region'"):
            neptune_driver(config)
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_neptune_driver_returns_graph(self, mock_neptune_session):
        """Test that neptune driver returns a ConjunctiveGraph."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        # Mock credentials
        mock_creds = Mock()
        mock_creds.access_key = 'test_key'
        mock_creds.secret_key = 'test_secret'
        mock_creds.token = None
        mock_neptune_session.return_value.get_credentials.return_value = mock_creds
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql',
            '_region': 'us-east-1'
        }
        
        graph = neptune_driver(config)
        
        assert isinstance(graph, ConjunctiveGraph)
        assert hasattr(graph.store, 'region_name')
        assert graph.store.region_name == 'us-east-1'
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_neptune_driver_with_custom_service_name(self, mock_neptune_session):
        """Test that neptune driver accepts custom service name."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        # Mock credentials
        mock_creds = Mock()
        mock_creds.access_key = 'test_key'
        mock_creds.secret_key = 'test_secret'
        mock_creds.token = None
        mock_neptune_session.return_value.get_credentials.return_value = mock_creds
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql',
            '_region': 'us-west-2',
            '_service_name': 'custom-service'
        }
        
        graph = neptune_driver(config)
        
        assert graph.store.service_name == 'custom-service'


class TestCreateQueryStoreWithNeptune:
    """Test create_neptune_query_store with Neptune stores."""
    
    @patch('whyis.plugins.neptune.neptune_sparql_store.boto3.Session')
    def test_create_query_store_for_neptune(self, mock_neptune_session):
        """Test that create_neptune_query_store creates Neptune store for Neptune source."""
        from whyis.plugins.neptune.plugin import create_neptune_query_store
        
        # Mock credentials
        mock_creds = Mock()
        mock_creds.access_key = 'test_key'
        mock_creds.secret_key = 'test_secret'
        mock_creds.token = None
        mock_neptune_session.return_value.get_credentials.return_value = mock_creds
        
        # Create a Neptune store
        source_store = NeptuneSPARQLUpdateStore(
            query_endpoint='https://neptune.example.com/sparql',
            update_endpoint='https://neptune.example.com/sparql',
            region_name='us-east-1'
        )
        
        # Create query store from it
        query_store = create_neptune_query_store(source_store)
        
        # Verify it's also a Neptune store with auth
        assert isinstance(query_store, NeptuneSPARQLStore)
        assert query_store._connector.region_name == 'us-east-1'
