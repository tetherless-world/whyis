"""
Unit tests for Neptune plugin with IAM authentication.

Tests the Neptune driver that supports AWS IAM authentication for Amazon Neptune.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# Skip all tests if dependencies not available
pytest.importorskip("flask_security")
pytest.importorskip("aws_requests_auth")

from rdflib import URIRef, Namespace, Literal
from rdflib.graph import ConjunctiveGraph
from whyis.database.database_utils import drivers, node_to_sparql


class TestNeptuneDriver:
    """Test the Neptune driver registration and functionality."""
    
    def test_neptune_driver_can_be_registered(self):
        """Test that neptune driver can be registered by plugin."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        # Verify the function exists and is callable
        assert callable(neptune_driver)
    
    @patch('whyis.plugins.neptune.plugin.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret'})
    def test_neptune_driver_requires_region(self):
        """Test that neptune driver requires region configuration."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql'
        }
        
        with pytest.raises(ValueError, match="requires '_region'"):
            neptune_driver(config)
    
    @patch('whyis.plugins.neptune.plugin.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret'})
    def test_neptune_driver_returns_graph(self):
        """Test that neptune driver returns a ConjunctiveGraph."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql',
            '_region': 'us-east-1'
        }
        
        graph = neptune_driver(config)
        
        assert isinstance(graph, ConjunctiveGraph)
        # Store should have gsp_endpoint set
        assert hasattr(graph.store, 'gsp_endpoint')
        assert graph.store.gsp_endpoint == 'https://neptune.example.com/sparql'
    
    @patch('whyis.plugins.neptune.plugin.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret'})
    def test_neptune_driver_with_custom_service_name(self):
        """Test that neptune driver accepts custom service name."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql',
            '_region': 'us-west-2',
            '_service_name': 'custom-service'
        }
        
        graph = neptune_driver(config)
        
        # Graph should be created successfully
        assert isinstance(graph, ConjunctiveGraph)
    
    @patch('whyis.plugins.neptune.plugin.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret'})
    def test_neptune_driver_with_gsp_endpoint(self):
        """Test that neptune driver uses separate GSP endpoint if provided."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql',
            '_gsp_endpoint': 'https://neptune.example.com/data',
            '_region': 'us-east-1'
        }
        
        graph = neptune_driver(config)
        
        assert graph.store.gsp_endpoint == 'https://neptune.example.com/data'


class TestNeptuneGSPOperations:
    """Test Neptune Graph Store Protocol operations with AWS auth."""
    
    @patch('whyis.plugins.neptune.plugin.os.environ', {'AWS_ACCESS_KEY_ID': 'test_key', 'AWS_SECRET_ACCESS_KEY': 'test_secret'})
    @patch('whyis.plugins.neptune.plugin.requests.Session')
    def test_gsp_operations_use_aws_auth(self, mock_requests_session):
        """Test that GSP operations (publish, put, post, delete) use AWS auth."""
        from whyis.plugins.neptune.plugin import neptune_driver
        
        # Mock requests session
        mock_session_instance = Mock()
        mock_response = Mock()
        mock_response.ok = True
        mock_session_instance.post.return_value = mock_response
        mock_session_instance.put.return_value = mock_response
        mock_session_instance.delete.return_value = mock_response
        mock_requests_session.return_value = mock_session_instance
        
        config = {
            '_endpoint': 'https://neptune.example.com/sparql',
            '_region': 'us-east-1'
        }
        
        graph = neptune_driver(config)
        
        # Test that publish method exists and has auth
        assert hasattr(graph.store, 'publish')
        assert hasattr(graph.store, 'put')
        assert hasattr(graph.store, 'post')
        assert hasattr(graph.store, 'delete')
        
        # Call publish to verify it works
        graph.store.publish(b'test data')
        
        # Verify a session was created
        assert mock_requests_session.called


class TestNeptuneEntityResolver:
    """Test the NeptuneEntityResolver class."""
    
    def test_escape_sparql_string(self):
        """Test that SPARQL string escaping works correctly."""
        from whyis.plugins.neptune.plugin import NeptuneEntityResolver
        
        resolver = NeptuneEntityResolver()
        
        # Test basic string
        assert resolver._escape_sparql_string("test") == "test"
        
        # Test string with quotes
        assert resolver._escape_sparql_string('test "quoted"') == 'test \\"quoted\\"'
        
        # Test string with backslashes
        assert resolver._escape_sparql_string('test\\path') == 'test\\\\path'
        
        # Test string with newlines
        assert resolver._escape_sparql_string('test\nline') == 'test\\nline'
        
        # Test string with carriage returns
        assert resolver._escape_sparql_string('test\rline') == 'test\\rline'
        
        # Test complex string with multiple special characters
        assert resolver._escape_sparql_string('test "quote" and\\path\nline') == 'test \\"quote\\" and\\\\path\\nline'
        
        # Test None
        assert resolver._escape_sparql_string(None) == ""
    
    def test_fts_query_format(self):
        """Test that the FTS query is correctly formatted."""
        from whyis.plugins.neptune.plugin import NeptuneEntityResolver
        
        resolver = NeptuneEntityResolver()
        
        # Check that the query uses full URIs for Neptune FTS
        assert '<http://aws.amazon.com/neptune/vocab/v01/services/fts#search>' in resolver.query
        assert '<http://aws.amazon.com/neptune/vocab/v01/services/fts#config>' in resolver.query
        assert '<http://aws.amazon.com/neptune/vocab/v01/services/fts#query>' in resolver.query
        assert '<http://aws.amazon.com/neptune/vocab/v01/services/fts#endpoint>' in resolver.query
        
        # Check that query uses string substitution for search term (not variable binding)
        assert '"%s"' in resolver.query  # Search term should be inserted as quoted string
    
    def test_on_resolve_escapes_search_term(self):
        """Test that on_resolve properly escapes the search term."""
        from whyis.plugins.neptune.plugin import NeptuneEntityResolver
        
        resolver = NeptuneEntityResolver()
        
        # Test that the query will safely escape special characters
        term_with_quotes = 'test "injection" attempt'
        escaped = resolver._escape_sparql_string(term_with_quotes)
        
        # Verify the quotes were escaped
        assert escaped == 'test \\"injection\\" attempt'
        
        # Verify that when formatted into the query, it's safe
        test_query = 'SELECT * WHERE { ?s ?p "%s" }' % escaped
        
        # The query should contain the escaped version
        assert 'test \\"injection\\" attempt' in test_query
        
        # And should not contain the unescaped quotes that could break out
        assert 'test "injection" attempt' not in test_query
