"""
Unit tests for whyis.database.database_utils module.

Tests utility functions for database operations.
"""

import pytest

# Skip all tests if dependencies not available
pytest.importorskip("flask_security")

from rdflib import BNode, URIRef, Literal
from whyis.database.database_utils import node_to_sparql, drivers


class TestNodeToSparql:
    """Test the node_to_sparql function."""
    
    def test_node_to_sparql_with_bnode(self):
        """Test node_to_sparql with a blank node."""
        bnode = BNode()
        result = node_to_sparql(bnode)
        
        assert result.startswith('<bnode:b')
        assert result.endswith('>')
    
    def test_node_to_sparql_with_uriref(self):
        """Test node_to_sparql with a URIRef."""
        uri = URIRef("http://example.com/resource")
        result = node_to_sparql(uri)
        
        assert '<http://example.com/resource>' in result
    
    def test_node_to_sparql_with_literal(self):
        """Test node_to_sparql with a Literal."""
        literal = Literal("test value")
        result = node_to_sparql(literal)
        
        # Should return a SPARQL literal representation
        assert isinstance(result, str)
        assert 'test value' in result or '"test value"' in result
    
    def test_node_to_sparql_with_typed_literal(self):
        """Test node_to_sparql with a typed Literal."""
        from rdflib import XSD
        literal = Literal(42, datatype=XSD.integer)
        result = node_to_sparql(literal)
        
        assert isinstance(result, str)
    
    def test_node_to_sparql_bnode_format(self):
        """Test that blank node format is correct."""
        bnode = BNode("test123")
        result = node_to_sparql(bnode)
        
        # Should convert to bnode: URI format
        assert result.startswith('<bnode:b')
        assert 'test123' in result
        assert result.endswith('>')
    
    def test_node_to_sparql_preserves_uri(self):
        """Test that URIRefs are properly formatted."""
        uri = URIRef("http://example.com/test#resource")
        result = node_to_sparql(uri)
        
        assert 'http://example.com/test#resource' in result
    
    def test_node_to_sparql_returns_string(self):
        """Test that node_to_sparql always returns a string."""
        nodes = [
            BNode(),
            URIRef("http://example.com/test"),
            Literal("test")
        ]
        
        for node in nodes:
            result = node_to_sparql(node)
            assert isinstance(result, str)


class TestDriverDecorator:
    """Test the driver decorator function."""
    
    def test_drivers_dict_exists(self):
        """Test that drivers dictionary exists."""
        assert isinstance(drivers, dict)
    
    def test_memory_driver_registered(self):
        """Test that memory driver is registered."""
        assert 'memory' in drivers
    
    def test_memory_driver_callable(self):
        """Test that memory driver is callable."""
        memory_driver = drivers.get('memory')
        assert callable(memory_driver)
    
    def test_memory_driver_returns_graph(self):
        """Test that memory driver returns a graph."""
        from rdflib.graph import ConjunctiveGraph
        memory_driver = drivers.get('memory')
        
        config = {}
        graph = memory_driver(config)
        
        assert isinstance(graph, ConjunctiveGraph)
