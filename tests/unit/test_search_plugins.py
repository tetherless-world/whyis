"""
Unit tests for search plugins (fuseki_search and neptune_search).

Tests both entity resolution and search functionality for Fuseki and Neptune backends.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import rdflib
from rdflib import Namespace, Literal, URIRef


class TestFusekiSearchPlugin(unittest.TestCase):
    """Test the FusekiSearchPlugin and FusekiEntityResolver."""

    def setUp(self):
        """Set up test fixtures."""
        from whyis.plugins.fuseki_search.plugin import FusekiEntityResolver, FusekiSearchPlugin
        self.resolver_class = FusekiEntityResolver
        self.plugin_class = FusekiSearchPlugin

    def test_resolver_init(self):
        """Test FusekiEntityResolver initialization."""
        resolver = self.resolver_class(database="test_db")
        self.assertEqual(resolver.database, "test_db")
        
        # Test default database
        resolver_default = self.resolver_class()
        self.assertEqual(resolver_default.database, "knowledge")

    def test_resolver_query_format(self):
        """Test that FusekiEntityResolver generates correct SPARQL queries."""
        resolver = self.resolver_class()
        
        # Check query structure contains text:search
        self.assertIn("text:search", resolver.query)
        self.assertIn("(?label ?relevance)", resolver.query)
        
        # Check for proper filtering
        self.assertIn("filter not exists", resolver.query)
        self.assertIn("np:Nanopublication", resolver.query)

    def test_resolver_type_query(self):
        """Test type filtering in queries."""
        resolver = self.resolver_class()
        type_uri = "http://example.org/TestType"
        type_query = resolver.type_query % type_uri
        
        self.assertIn("rdf:type", type_query)
        self.assertIn(type_uri, type_query)

    def test_resolver_context_query(self):
        """Test context filtering in queries."""
        resolver = self.resolver_class()
        context = "test context"
        context_query = resolver.context_query % context
        
        self.assertIn("text:search", context_query)
        self.assertIn("optional", context_query.lower())

    def test_resolver_on_resolve_basic(self):
        """Test basic entity resolution."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
            
            # Mock the database and query results
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
            
            # Mock query result
            mock_result = Mock()
            mock_result.asdict.return_value = {
                'node': 'http://example.org/entity1',
                'label': 'Test Entity',
                'types': 'http://example.org/Type1||http://example.org/Type2',
                'score': 1.0
            }
            mock_graph.query.return_value = [mock_result]
            
            # Mock labelize
            mock_app.labelize.side_effect = lambda d, k, v: d.update({v: 'Labeled'})
            
            results = resolver.on_resolve("test", label=False)
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['node'], 'http://example.org/entity1')
            self.assertIn('types', results[0])
            self.assertEqual(len(results[0]['types']), 2)

    def test_resolver_on_resolve_with_type(self):
        """Test entity resolution with type filtering."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
            
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
            mock_graph.query.return_value = []
            
            type_uri = "http://example.org/TestType"
            results = resolver.on_resolve("test", type=type_uri, label=False)
            
            # Verify query was called
            mock_graph.query.assert_called_once()
            call_args = mock_graph.query.call_args[0][0]
            
            # Check that type filter is in query
            self.assertIn(type_uri, call_args)

    def test_resolver_on_resolve_with_context(self):
        """Test entity resolution with context."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
            
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
            mock_graph.query.return_value = []
            
            context = "test context"
            results = resolver.on_resolve("test", context=context, label=False)
            
            # Verify query was called
            mock_graph.query.assert_called_once()
            call_args = mock_graph.query.call_args[0][0]
            
            # Check that context is in query
            self.assertIn(context, call_args)

    def test_plugin_resolvers_dict(self):
        """Test that plugin has correct resolver mappings."""
        plugin = self.plugin_class()
        
        self.assertIn("fuseki", plugin.resolvers)
        self.assertIn("sparql", plugin.resolvers)
        self.assertEqual(plugin.resolvers["fuseki"], self.resolver_class)
        self.assertEqual(plugin.resolvers["sparql"], self.resolver_class)

    def test_plugin_create_blueprint(self):
        """Test plugin blueprint creation."""
        with patch('whyis.plugins.fuseki_search.plugin.PluginBlueprint') as mock_blueprint:
            plugin = self.plugin_class()
            blueprint = plugin.create_blueprint()
            
            # Verify PluginBlueprint was called with correct arguments
            mock_blueprint.assert_called_once_with('fuseki_search', 
                                                   'whyis.plugins.fuseki_search.plugin',
                                                   template_folder='templates')

    def test_plugin_init_valid_type(self):
        """Test plugin initialization with valid resolver type."""
        plugin = self.plugin_class()
        mock_app = Mock()
        plugin.app = mock_app
        mock_app.config.get.side_effect = lambda k, d: {'RESOLVER_TYPE': 'fuseki', 
                                                          'RESOLVER_DB': 'knowledge'}.get(k, d)
        
        plugin.init()
        
        # Verify add_listener was called
        mock_app.add_listener.assert_called_once()

    def test_plugin_init_invalid_type(self):
        """Test plugin initialization with invalid resolver type."""
        plugin = self.plugin_class()
        mock_app = Mock()
        plugin.app = mock_app
        mock_app.config.get.side_effect = lambda k, d: {'RESOLVER_TYPE': 'invalid', 
                                                          'RESOLVER_DB': 'knowledge'}.get(k, d)
        
        # Should raise ValueError for invalid type
        with self.assertRaises(ValueError) as context:
            plugin.init()
        
        self.assertIn("Invalid RESOLVER_TYPE", str(context.exception))


class TestNeptuneSearchPlugin(unittest.TestCase):
    """Test the NeptuneSearchPlugin and NeptuneEntityResolver."""

    def setUp(self):
        """Set up test fixtures."""
        from whyis.plugins.neptune_search.plugin import NeptuneEntityResolver, NeptuneSearchPlugin
        self.resolver_class = NeptuneEntityResolver
        self.plugin_class = NeptuneSearchPlugin

    def test_resolver_init(self):
        """Test NeptuneEntityResolver initialization."""
        resolver = self.resolver_class(database="test_db")
        self.assertEqual(resolver.database, "test_db")
        
        # Test default database
        resolver_default = self.resolver_class()
        self.assertEqual(resolver_default.database, "knowledge")

    def test_resolver_query_format(self):
        """Test that NeptuneEntityResolver generates correct SPARQL queries."""
        resolver = self.resolver_class()
        
        # Check query structure contains SERVICE clause and fts:search
        self.assertIn("SERVICE ftsEndpoint", resolver.query)
        self.assertIn("fts:search", resolver.query)
        self.assertIn("fts:matchQuery", resolver.query)
        self.assertIn("fts:entity", resolver.query)
        self.assertIn("fts:score", resolver.query)
        
        # Check for proper filtering
        self.assertIn("filter not exists", resolver.query)
        self.assertIn("np:Nanopublication", resolver.query)

    def test_resolver_service_clause(self):
        """Test that SERVICE clause is properly formatted."""
        resolver = self.resolver_class()
        
        # Verify SERVICE clause structure
        self.assertIn("SERVICE ftsEndpoint", resolver.query)
        self.assertIn("[] fts:search", resolver.query)
        
        # Check context query also uses SERVICE
        self.assertIn("SERVICE ftsEndpoint", resolver.context_query)

    def test_resolver_type_query(self):
        """Test type filtering in queries."""
        resolver = self.resolver_class()
        type_uri = "http://example.org/TestType"
        type_query = resolver.type_query % type_uri
        
        self.assertIn("rdf:type", type_query)
        self.assertIn(type_uri, type_query)

    def test_resolver_context_query(self):
        """Test context filtering in queries."""
        resolver = self.resolver_class()
        context = "test context"
        context_query = resolver.context_query % (context, context)
        
        self.assertIn("fts:search", context_query)
        self.assertIn("fts:matchQuery", context_query)
        self.assertIn("optional", context_query.lower())

    # Removed patch decorator
    def test_resolver_on_resolve_basic(self):
        """Test basic entity resolution."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
        
            # Mock the database and query results
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
        
            # Mock query result
            mock_result = Mock()
            mock_result.asdict.return_value = {
                'node': 'http://example.org/entity1',
                'label': 'Test Entity',
                'types': 'http://example.org/Type1||http://example.org/Type2',
                'score': 1.0
            }
            mock_graph.query.return_value = [mock_result]
        
            # Mock labelize
            mock_app.labelize.side_effect = lambda d, k, v: d.update({v: 'Labeled'})
        
            results = resolver.on_resolve("test", label=False)
        
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['node'], 'http://example.org/entity1')
            self.assertIn('types', results[0])
            self.assertEqual(len(results[0]['types']), 2)

        # Removed patch decorator
    def test_resolver_on_resolve_with_empty_types(self):
        """Test entity resolution handles empty types correctly."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
        
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
        
            # Mock query result with empty types
            mock_result = Mock()
            mock_result.asdict.return_value = {
                'node': 'http://example.org/entity1',
                'label': 'Test Entity',
                'types': '',  # Empty types string
                'score': 1.0
            }
            mock_graph.query.return_value = [mock_result]
        
            results = resolver.on_resolve("test", label=False)
        
            # Should handle empty types gracefully
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0]['types'], [])

        # Removed patch decorator
    def test_resolver_on_resolve_with_type(self):
        """Test entity resolution with type filtering."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
        
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
            mock_graph.query.return_value = []
        
            type_uri = "http://example.org/TestType"
            results = resolver.on_resolve("test", type=type_uri, label=False)
        
            # Verify query was called
            mock_graph.query.assert_called_once()
            call_args = mock_graph.query.call_args[0][0]
        
            # Check that type filter is in query
            self.assertIn(type_uri, call_args)

        # Removed patch decorator
    def test_resolver_on_resolve_with_context(self):
        """Test entity resolution with context."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
        
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
            mock_graph.query.return_value = []
        
            context = "test context"
            results = resolver.on_resolve("test", context=context, label=False)
        
            # Verify query was called
            mock_graph.query.assert_called_once()
            call_args = mock_graph.query.call_args[0][0]
        
            # Check that context is in query (appears twice for matchQuery)
            self.assertEqual(call_args.count(context), 2)

        # Removed patch decorator
    def test_resolver_match_query_parameter(self):
        """Test that matchQuery parameter is included correctly."""
        with patch('flask.current_app') as mock_app:
            resolver = self.resolver_class()
        
            mock_graph = Mock()
            mock_app.databases = {"knowledge": mock_graph}
            mock_graph.query.return_value = []
        
            results = resolver.on_resolve("test", label=False)
        
            # Verify query was called
            mock_graph.query.assert_called_once()
            call_args = mock_graph.query.call_args[0][0]
        
            # Check that matchQuery with '*' is in query
            self.assertIn("fts:matchQuery '*'", call_args)

    def test_plugin_resolvers_dict(self):
        """Test that plugin has correct resolver mappings."""
        plugin = self.plugin_class()
        
        self.assertIn("neptune", plugin.resolvers)
        self.assertEqual(plugin.resolvers["neptune"], self.resolver_class)

    def test_plugin_create_blueprint(self):
        """Test plugin blueprint creation."""
        with patch('whyis.plugins.neptune_search.plugin.PluginBlueprint') as mock_blueprint:
            plugin = self.plugin_class()
            blueprint = plugin.create_blueprint()
            
            # Verify PluginBlueprint was called with correct arguments
            mock_blueprint.assert_called_once_with('neptune_search',
                                                   'whyis.plugins.neptune_search.plugin',
                                                   template_folder='templates')

    # Removed patch decorator
    def test_plugin_init_valid_type(self):
        """Test plugin initialization with valid resolver type."""
        mock_app = Mock()
        plugin = self.plugin_class()
        plugin.app = mock_app
        mock_app.config.get.side_effect = lambda k, d: {'RESOLVER_TYPE': 'neptune',
                                                          'RESOLVER_DB': 'knowledge'}.get(k, d)
        
        plugin.init()
        
        # Verify add_listener was called
        mock_app.add_listener.assert_called_once()

    # Removed patch decorator
    def test_plugin_init_invalid_type_silent(self):
        """Test plugin initialization silently skips invalid resolver type."""
        mock_app = Mock()
        plugin = self.plugin_class()
        plugin.app = mock_app
        mock_app.config.get.side_effect = lambda k, d: {'RESOLVER_TYPE': 'fuseki',
                                                          'RESOLVER_DB': 'knowledge'}.get(k, d)
        
        # Should not raise, should silently skip
        plugin.init()
        
        # Verify add_listener was NOT called
        mock_app.add_listener.assert_not_called()


class TestSearchPluginIntegration(unittest.TestCase):
    """Integration tests comparing Fuseki and Neptune plugins."""

    def test_both_plugins_have_same_interface(self):
        """Test that both plugins implement the same interface."""
        from whyis.plugins.fuseki_search.plugin import FusekiEntityResolver
        from whyis.plugins.neptune_search.plugin import NeptuneEntityResolver
        
        fuseki_methods = {m for m in dir(FusekiEntityResolver) if not m.startswith('_')}
        neptune_methods = {m for m in dir(NeptuneEntityResolver) if not m.startswith('_')}
        
        # Both should have on_resolve method
        self.assertIn('on_resolve', fuseki_methods)
        self.assertIn('on_resolve', neptune_methods)

    def test_both_plugins_filter_same_types(self):
        """Test that both plugins filter the same resource types."""
        from whyis.plugins.fuseki_search.plugin import FusekiEntityResolver
        from whyis.plugins.neptune_search.plugin import NeptuneEntityResolver
        
        fuseki = FusekiEntityResolver()
        neptune = NeptuneEntityResolver()
        
        # Both should filter nanopublication types
        self.assertIn("np:Nanopublication", fuseki.query)
        self.assertIn("np:Nanopublication", neptune.query)
        
        self.assertIn("np:Assertion", fuseki.query)
        self.assertIn("np:Assertion", neptune.query)

    def test_prefixes_compatibility(self):
        """Test that both plugins define compatible prefixes."""
        from whyis.plugins.fuseki_search.plugin import prefixes as fuseki_prefixes
        from whyis.plugins.neptune_search.plugin import prefixes as neptune_prefixes
        
        # Common prefixes should exist
        common_keys = ['skos', 'foaf', 'schema', 'owl', 'rdfs', 'rdf', 'dc']
        
        for key in common_keys:
            self.assertIn(key, fuseki_prefixes)
            self.assertIn(key, neptune_prefixes)


if __name__ == '__main__':
    unittest.main()
