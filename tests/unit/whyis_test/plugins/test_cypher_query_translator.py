import unittest
from unittest.mock import Mock, patch, MagicMock
import rdflib
from whyis.plugins.cypher_query_translator.plugin import (
    CypherToSparqlTranslator,
    CypherQueryResolver,
    CypherQueryListener,
    CypherQueryPlugin
)


class TestCypherToSparqlTranslator(unittest.TestCase):
    """Test cases for the Cypher to SPARQL translator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {
            "Person": "http://schema.org/Person",
            "name": "http://schema.org/name",
            "age": "http://schema.org/age",
            "knows": "http://schema.org/knows",
            "ex": "http://example.org/"
        }
        self.translator = CypherToSparqlTranslator(self.context)
        
    def test_expand_uri_with_context(self):
        """Test URI expansion using JSON-LD context."""
        # Test simple term expansion
        self.assertEqual(
            self.translator.expand_uri("Person"),
            "http://schema.org/Person"
        )
        
        # Test prefixed term expansion
        self.assertEqual(
            self.translator.expand_uri("ex:test"),
            "http://example.org/test"
        )
        
        # Test term without mapping
        self.assertEqual(
            self.translator.expand_uri("unknown"),
            "unknown"
        )
        
    def test_extract_match_clause(self):
        """Test extraction of MATCH clause from Cypher query."""
        query = "MATCH (n:Person) WHERE n.name = 'John' RETURN n"
        match_clause = self.translator._extract_match_clause(query)
        self.assertEqual(match_clause, "(n:Person)")
        
        # Test complex match
        query = "MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN a, b"
        match_clause = self.translator._extract_match_clause(query)
        self.assertEqual(match_clause, "(a:Person)-[:KNOWS]->(b:Person)")
        
    def test_extract_where_clause(self):
        """Test extraction of WHERE clause from Cypher query."""
        query = "MATCH (n:Person) WHERE n.name = 'John' RETURN n"
        where_clause = self.translator._extract_where_clause(query)
        self.assertEqual(where_clause, "n.name = 'John'")
        
        # Test query without WHERE
        query = "MATCH (n:Person) RETURN n"
        where_clause = self.translator._extract_where_clause(query)
        self.assertEqual(where_clause, "")
        
    def test_extract_return_clause(self):
        """Test extraction of RETURN clause from Cypher query."""
        query = "MATCH (n:Person) RETURN n.name, n.age"
        return_clause = self.translator._extract_return_clause(query)
        self.assertEqual(return_clause, "n.name, n.age")
        
    def test_parse_return_clause(self):
        """Test parsing of RETURN clause to SPARQL SELECT."""
        # Test simple variable
        select_vars = self.translator._parse_return_clause("n")
        self.assertEqual(select_vars, "?n")
        
        # Test property access
        select_vars = self.translator._parse_return_clause("n.name, n.age")
        self.assertEqual(select_vars, "?n_name ?n_age")
        
        # Test empty return
        select_vars = self.translator._parse_return_clause("")
        self.assertEqual(select_vars, "*")
        
    def test_parse_match_clause_simple_node(self):
        """Test parsing of simple node patterns."""
        patterns = self.translator._parse_match_clause("(n:Person)")
        expected = "?n rdf:type <http://schema.org/Person> ."
        self.assertIn(expected, patterns)
        
    def test_parse_match_clause_node_without_label(self):
        """Test parsing of node without label."""
        patterns = self.translator._parse_match_clause("(n)")
        expected = "?n ?pn ?on ."
        self.assertIn(expected, patterns)
        
    def test_parse_where_clause_property_filter(self):
        """Test parsing of WHERE clause property filters."""
        filters = self.translator._parse_where_clause("n.name = 'John'")
        expected = 'FILTER(?n_name = "John")'
        self.assertIn(expected, filters)
        
    def test_translate_simple_cypher_query(self):
        """Test translation of a simple Cypher query."""
        cypher = "MATCH (n:Person) WHERE n.name = 'John' RETURN n"
        sparql = self.translator.translate(cypher)
        
        # Check that essential parts are present
        self.assertIn("SELECT ?n", sparql)
        self.assertIn("?n rdf:type <http://schema.org/Person>", sparql)
        self.assertIn('FILTER(?n_name = "John")', sparql)
        
    def test_translate_complex_cypher_query(self):
        """Test translation of a more complex Cypher query."""
        cypher = "MATCH (a:Person)-[:KNOWS]->(b:Person) RETURN a.name, b.name"
        sparql = self.translator.translate(cypher)
        
        # Check that variables are correctly selected
        self.assertIn("SELECT ?a_name ?b_name", sparql)
        
    def test_parse_property_patterns_with_reification(self):
        """Test parsing of property patterns with RDF reification."""
        patterns = self.translator._parse_property_patterns("{name: 'John'}")
        
        # Check reification statements
        self.assertIn("?stmt rdf:type rdf:Statement .", patterns)
        self.assertIn("?stmt rdf:subject ?s .", patterns)
        self.assertIn("?stmt rdf:predicate <http://schema.org/name> .", patterns)
        self.assertIn('?stmt rdf:object "John" .', patterns)


class TestCypherQueryResolver(unittest.TestCase):
    """Test cases for the Cypher query resolver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.context = {"Person": "http://schema.org/Person"}
        
        # Mock Flask app and current_app
        self.mock_app = Mock()
        self.mock_graph = Mock()
        self.mock_app.databases = {"knowledge": self.mock_graph}
        
    def test_resolver_initialization(self):
        """Test resolver initialization."""
        resolver = CypherQueryResolver("knowledge", self.context)
        
        self.assertEqual(resolver.database, "knowledge")
        self.assertEqual(resolver.translator.context, self.context)
        
    def test_on_cypher_query_success(self):
        """Test successful Cypher query execution."""
        with patch('whyis.plugins.cypher_query_translator.plugin.current_app') as mock_current_app:
            mock_current_app.databases = {"knowledge": self.mock_graph}
            mock_current_app.logger = Mock()
            
            # Mock query results
            mock_result = Mock()
            mock_result.asdict.return_value = {"n": "http://example.org/john"}
            self.mock_graph.query.return_value = [mock_result]
            
            resolver = CypherQueryResolver("knowledge", self.context)
            
            results = resolver.on_cypher_query("MATCH (n:Person) RETURN n")
            
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0], {"n": "http://example.org/john"})
        
    def test_on_cypher_query_with_context_update(self):
        """Test Cypher query with context update."""
        with patch('whyis.plugins.cypher_query_translator.plugin.current_app') as mock_current_app:
            mock_current_app.databases = {"knowledge": self.mock_graph}
            mock_current_app.logger = Mock()
            
            self.mock_graph.query.return_value = []
            
            resolver = CypherQueryResolver("knowledge", self.context)
            
            new_context = {"Employee": "http://schema.org/Employee"}
            resolver.on_cypher_query("MATCH (n:Employee) RETURN n", new_context)
            
            # Check that context was updated
            self.assertIn("Employee", resolver.translator.context)
            self.assertEqual(
                resolver.translator.context["Employee"],
                "http://schema.org/Employee"
            )
        
    def test_on_cypher_query_error_handling(self):
        """Test error handling in query execution."""
        with patch('whyis.plugins.cypher_query_translator.plugin.current_app') as mock_current_app:
            mock_current_app.databases = {"knowledge": self.mock_graph}
            mock_current_app.logger = Mock()
            
            # Make query raise an exception
            self.mock_graph.query.side_effect = Exception("Query failed")
            
            resolver = CypherQueryResolver("knowledge", self.context)
            
            results = resolver.on_cypher_query("INVALID QUERY")
            
            self.assertEqual(results, [])
            mock_current_app.logger.error.assert_called_once()


class TestCypherQueryPlugin(unittest.TestCase):
    """Test cases for the Cypher query plugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_app = Mock()
        self.mock_app.config = {
            'CYPHER_DB': 'test_db',
            'CYPHER_JSONLD_CONTEXT': {'Person': 'http://schema.org/Person'}
        }
        self.mock_app.listeners = []
        
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = CypherQueryPlugin(None, self.mock_app)
        
        plugin.init()
        
        # Check that listener was added
        self.mock_app.add_listener.assert_called_once()
        
        # Check that the listener is a CypherQueryResolver
        call_args = self.mock_app.add_listener.call_args[0]
        listener = call_args[0]
        self.assertIsInstance(listener, CypherQueryResolver)
        self.assertEqual(listener.database, 'test_db')
        
    def test_plugin_default_config(self):
        """Test plugin with default configuration."""
        # Remove custom config
        self.mock_app.config = {}
        
        plugin = CypherQueryPlugin(None, self.mock_app)
        
        plugin.init()
        
        # Check that defaults were used
        call_args = self.mock_app.add_listener.call_args[0]
        listener = call_args[0]
        self.assertEqual(listener.database, 'knowledge')
        self.assertEqual(listener.translator.context, {})
        
    def test_handle_cypher_query_success(self):
        """Test HTTP handler for Cypher queries."""
        with patch('whyis.plugins.cypher_query_translator.plugin.request') as mock_request, \
             patch('whyis.plugins.cypher_query_translator.plugin.jsonify') as mock_jsonify:
            
            # Setup
            plugin = CypherQueryPlugin(None, self.mock_app)
            
            mock_resolver = Mock(spec=CypherQueryResolver)
            mock_resolver.on_cypher_query.return_value = [{'n': 'result'}]
            self.mock_app.listeners = [mock_resolver]
            
            mock_request.get_json.return_value = {
                'query': 'MATCH (n) RETURN n',
                'context': {'Person': 'http://schema.org/Person'}
            }
            
            mock_jsonify.return_value = Mock()
            
            # Execute
            result = plugin._handle_cypher_query()
            
            # Verify
            mock_resolver.on_cypher_query.assert_called_once_with(
                'MATCH (n) RETURN n',
                {'Person': 'http://schema.org/Person'}
            )
            mock_jsonify.assert_called_once_with({'results': [{'n': 'result'}]})
        
    def test_handle_cypher_query_missing_query(self):
        """Test HTTP handler with missing query parameter."""
        with patch('whyis.plugins.cypher_query_translator.plugin.request') as mock_request, \
             patch('whyis.plugins.cypher_query_translator.plugin.jsonify') as mock_jsonify:
            
            plugin = CypherQueryPlugin(None, self.mock_app)
            
            mock_request.get_json.return_value = {}
            mock_jsonify.return_value = (Mock(), 400)
            
            result = plugin._handle_cypher_query()
            
            mock_jsonify.assert_called_once_with({'error': 'Missing query parameter'})
        
    def test_handle_cypher_query_no_resolver(self):
        """Test HTTP handler with no resolver available."""
        with patch('whyis.plugins.cypher_query_translator.plugin.request') as mock_request, \
             patch('whyis.plugins.cypher_query_translator.plugin.jsonify') as mock_jsonify:
            
            plugin = CypherQueryPlugin(None, self.mock_app)
            self.mock_app.listeners = []  # No resolver
            
            mock_request.get_json.return_value = {'query': 'MATCH (n) RETURN n'}
            mock_jsonify.return_value = (Mock(), 500)
            
            result = plugin._handle_cypher_query()
            
            mock_jsonify.assert_called_once_with({'error': 'Cypher resolver not found'})


class TestCypherQueryIntegration(unittest.TestCase):
    """Integration tests for Cypher query functionality."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.context = {
            "Person": "http://schema.org/Person",
            "name": "http://schema.org/name",
            "knows": "http://schema.org/knows"
        }
        
    def test_full_translation_workflow(self):
        """Test the complete translation workflow."""
        translator = CypherToSparqlTranslator(self.context)
        
        cypher_query = """
        MATCH (person:Person)
        WHERE person.name = 'Alice'
        RETURN person.name
        """
        
        sparql_query = translator.translate(cypher_query)
        
        # Verify essential SPARQL components
        self.assertIn("PREFIX", sparql_query)
        self.assertIn("SELECT ?person_name", sparql_query)
        self.assertIn("WHERE {", sparql_query)
        self.assertIn("?person rdf:type <http://schema.org/Person>", sparql_query)
        self.assertIn('FILTER(?person_name = "Alice")', sparql_query)
        
    def test_reification_patterns(self):
        """Test RDF reification for property statements."""
        translator = CypherToSparqlTranslator(self.context)
        
        patterns = translator._parse_property_patterns("{name: 'John', age: '30'}")
        
        # Should create reification statements for each property
        reification_statements = [p for p in patterns if 'rdf:Statement' in p]
        self.assertTrue(len(reification_statements) > 0)
        
        # Should include subject, predicate, and object statements
        subject_statements = [p for p in patterns if 'rdf:subject' in p]
        predicate_statements = [p for p in patterns if 'rdf:predicate' in p]
        object_statements = [p for p in patterns if 'rdf:object' in p]
        
        self.assertTrue(len(subject_statements) > 0)
        self.assertTrue(len(predicate_statements) > 0)
        self.assertTrue(len(object_statements) > 0)


if __name__ == '__main__':
    unittest.main()