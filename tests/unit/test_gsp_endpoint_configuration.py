"""
Unit tests for GSP endpoint configuration in database_utils module.

Tests that Graph Store Protocol (GSP) endpoint can be configured separately
from the SPARQL query endpoint.
"""

import pytest

# Skip all tests if dependencies not available
pytest.importorskip("flask_security")

from unittest.mock import Mock, patch, MagicMock
from rdflib import URIRef, ConjunctiveGraph, Graph
from whyis.database.database_utils import sparql_driver, _remote_sparql_store_protocol


class TestGSPEndpointConfiguration:
    """Test GSP endpoint configuration functionality."""
    
    def test_sparql_driver_with_separate_gsp_endpoint(self):
        """Test that sparql_driver sets gsp_endpoint when provided in config."""
        config = {
            "_endpoint": "http://localhost:3030/dataset/sparql",
            "_gsp_endpoint": "http://localhost:3030/dataset/data"
        }
        
        graph = sparql_driver(config)
        
        # Verify the store has both endpoints set correctly
        assert graph.store.query_endpoint == "http://localhost:3030/dataset/sparql"
        assert graph.store.gsp_endpoint == "http://localhost:3030/dataset/data"
    
    def test_sparql_driver_without_gsp_endpoint_falls_back_to_query_endpoint(self):
        """Test that sparql_driver falls back to query_endpoint when gsp_endpoint not provided."""
        config = {
            "_endpoint": "http://localhost:3030/dataset/sparql"
        }
        
        graph = sparql_driver(config)
        
        # Verify the store uses query_endpoint for gsp_endpoint when not specified
        assert graph.store.query_endpoint == "http://localhost:3030/dataset/sparql"
        assert graph.store.gsp_endpoint == "http://localhost:3030/dataset/sparql"
    
    def test_sparql_driver_with_auth_credentials(self):
        """Test that sparql_driver properly configures auth with separate gsp_endpoint."""
        config = {
            "_endpoint": "http://localhost:3030/dataset/sparql",
            "_gsp_endpoint": "http://localhost:3030/dataset/data",
            "_username": "user",
            "_password": "pass"
        }
        
        graph = sparql_driver(config)
        
        # Verify auth is set
        assert graph.store.auth == ("user", "pass")
        assert graph.store.gsp_endpoint == "http://localhost:3030/dataset/data"
    
    def test_sparql_driver_with_default_graph(self):
        """Test that sparql_driver handles default_graph with gsp_endpoint."""
        config = {
            "_endpoint": "http://localhost:3030/dataset/sparql",
            "_gsp_endpoint": "http://localhost:3030/dataset/data",
            "_default_graph": "http://example.com/graph"
        }
        
        graph = sparql_driver(config)
        
        # Verify the graph is a ConjunctiveGraph
        assert isinstance(graph, ConjunctiveGraph)
        assert graph.store.gsp_endpoint == "http://localhost:3030/dataset/data"


class TestRemoteSPARQLStoreProtocolGSP:
    """Test that GSP operations use the gsp_endpoint."""
    
    @patch('whyis.database.database_utils.requests.session')
    def test_publish_uses_gsp_endpoint(self, mock_session):
        """Test that publish operation uses gsp_endpoint."""
        mock_response = Mock()
        mock_response.ok = True
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a mock store with different endpoints
        store = Mock()
        store.query_endpoint = "http://localhost:3030/dataset/sparql"
        store.gsp_endpoint = "http://localhost:3030/dataset/data"
        store.auth = None
        
        # Apply the protocol
        store = _remote_sparql_store_protocol(store)
        
        # Call publish
        test_data = "<http://example.com/s> <http://example.com/p> <http://example.com/o> ."
        store.publish(test_data)
        
        # Verify POST was called with gsp_endpoint, not query_endpoint
        mock_session_instance.post.assert_called_once()
        call_args = mock_session_instance.post.call_args
        assert call_args[0][0] == "http://localhost:3030/dataset/data"
    
    @patch('whyis.database.database_utils.requests.session')
    def test_put_uses_gsp_endpoint(self, mock_session):
        """Test that put operation uses gsp_endpoint."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.text = "Success"
        mock_response.status_code = 200
        mock_session_instance = Mock()
        mock_session_instance.put.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a mock store with different endpoints
        store = Mock()
        store.query_endpoint = "http://localhost:3030/dataset/sparql"
        store.gsp_endpoint = "http://localhost:3030/dataset/data"
        store.auth = None
        
        # Apply the protocol
        store = _remote_sparql_store_protocol(store)
        
        # Create a mock graph
        mock_graph = Mock()
        mock_graph.identifier = URIRef("http://example.com/graph")
        mock_graph.store = store
        
        # Mock ConjunctiveGraph and serialize
        with patch('whyis.database.database_utils.ConjunctiveGraph') as mock_cg:
            mock_cg_instance = Mock()
            mock_cg_instance.serialize.return_value = "serialized data"
            mock_cg.return_value = mock_cg_instance
            
            # Call put
            store.put(mock_graph)
            
            # Verify PUT was called with gsp_endpoint
            mock_session_instance.put.assert_called_once()
            call_args = mock_session_instance.put.call_args
            assert call_args[0][0] == "http://localhost:3030/dataset/data"
    
    @patch('whyis.database.database_utils.requests.session')
    def test_post_uses_gsp_endpoint(self, mock_session):
        """Test that post operation uses gsp_endpoint."""
        mock_response = Mock()
        mock_response.ok = True
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a mock store with different endpoints
        store = Mock()
        store.query_endpoint = "http://localhost:3030/dataset/sparql"
        store.gsp_endpoint = "http://localhost:3030/dataset/data"
        store.auth = None
        
        # Apply the protocol
        store = _remote_sparql_store_protocol(store)
        
        # Create a mock graph
        mock_graph = Mock()
        mock_graph.store = store
        
        # Mock ConjunctiveGraph and serialize
        with patch('whyis.database.database_utils.ConjunctiveGraph') as mock_cg:
            mock_cg_instance = Mock()
            mock_cg_instance.serialize.return_value = "serialized data"
            mock_cg.return_value = mock_cg_instance
            
            # Call post
            store.post(mock_graph)
            
            # Verify POST was called with gsp_endpoint
            mock_session_instance.post.assert_called_once()
            call_args = mock_session_instance.post.call_args
            assert call_args[0][0] == "http://localhost:3030/dataset/data"
    
    @patch('whyis.database.database_utils.requests.session')
    def test_delete_uses_gsp_endpoint(self, mock_session):
        """Test that delete operation uses gsp_endpoint."""
        mock_response = Mock()
        mock_response.ok = True
        mock_session_instance = Mock()
        mock_session_instance.delete.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a mock store with different endpoints
        store = Mock()
        store.query_endpoint = "http://localhost:3030/dataset/sparql"
        store.gsp_endpoint = "http://localhost:3030/dataset/data"
        store.auth = None
        
        # Apply the protocol
        store = _remote_sparql_store_protocol(store)
        
        # Call delete
        store.delete(URIRef("http://example.com/graph"))
        
        # Verify DELETE was called with gsp_endpoint
        mock_session_instance.delete.assert_called_once()
        call_args = mock_session_instance.delete.call_args
        assert call_args[0][0] == "http://localhost:3030/dataset/data"
    
    @patch('whyis.database.database_utils.requests.session')
    def test_operations_with_auth(self, mock_session):
        """Test that GSP operations include auth when configured."""
        mock_response = Mock()
        mock_response.ok = True
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a mock store with auth
        store = Mock()
        store.query_endpoint = "http://localhost:3030/dataset/sparql"
        store.gsp_endpoint = "http://localhost:3030/dataset/data"
        store.auth = ("user", "password")
        
        # Apply the protocol
        store = _remote_sparql_store_protocol(store)
        
        # Call publish
        test_data = "<http://example.com/s> <http://example.com/p> <http://example.com/o> ."
        store.publish(test_data)
        
        # Verify auth was passed
        call_kwargs = mock_session_instance.post.call_args[1]
        assert 'auth' in call_kwargs
        assert call_kwargs['auth'] == ("user", "password")


class TestBackwardCompatibility:
    """Test that existing configurations without gsp_endpoint continue to work."""
    
    def test_existing_config_without_gsp_endpoint_works(self):
        """Test that configurations without _gsp_endpoint still work (backward compatibility)."""
        config = {
            "_endpoint": "http://localhost:3030/dataset/sparql"
        }
        
        # This should not raise an error
        graph = sparql_driver(config)
        
        # Both endpoints should be the same (fallback behavior)
        assert graph.store.query_endpoint == graph.store.gsp_endpoint
        assert graph.store.gsp_endpoint == "http://localhost:3030/dataset/sparql"
    
    @patch('whyis.database.database_utils.requests.session')
    def test_gsp_operations_work_with_fallback_endpoint(self, mock_session):
        """Test that GSP operations work when using fallback endpoint."""
        mock_response = Mock()
        mock_response.ok = True
        mock_session_instance = Mock()
        mock_session_instance.post.return_value = mock_response
        mock_session.return_value = mock_session_instance
        
        # Create a store with only query_endpoint (simulating old config)
        config = {
            "_endpoint": "http://localhost:3030/dataset/sparql"
        }
        graph = sparql_driver(config)
        
        # Verify the store has gsp_endpoint set to query_endpoint
        assert graph.store.gsp_endpoint == graph.store.query_endpoint
        
        # Call publish to ensure it works
        test_data = "<http://example.com/s> <http://example.com/p> <http://example.com/o> ."
        graph.store.publish(test_data)
        
        # Verify POST was called (should work without errors)
        mock_session_instance.post.assert_called_once()
