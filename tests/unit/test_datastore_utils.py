"""
Unit tests for whyis.datastore.datastore_utils module.

Tests utility functions for datastore operations.
"""

import pytest
import re
import sys
import os

# Add whyis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from rdflib import BNode, Literal, URIRef

# Import directly from the module file to avoid __init__ dependencies
import importlib.util
spec = importlib.util.spec_from_file_location(
    "datastore_utils",
    os.path.join(os.path.dirname(__file__), '../../whyis/datastore/datastore_utils.py')
)
datastore_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(datastore_utils)

create_id = datastore_utils.create_id
value2object = datastore_utils.value2object


class TestCreateId:
    """Test the create_id function."""
    
    def test_create_id_returns_string(self):
        """Test that create_id returns a string."""
        result = create_id()
        assert isinstance(result, str)
    
    def test_create_id_not_empty(self):
        """Test that create_id returns non-empty string."""
        result = create_id()
        assert len(result) > 0
    
    def test_create_id_is_base64(self):
        """Test that create_id returns base64-like string."""
        result = create_id()
        # Base64 strings contain alphanumeric and +/
        assert re.match(r'^[A-Za-z0-9+/]+$', result)
    
    def test_create_id_no_trailing_equals(self):
        """Test that create_id removes trailing equals signs."""
        result = create_id()
        assert not result.endswith('=')
    
    def test_create_id_no_trailing_newline(self):
        """Test that create_id removes trailing newlines."""
        result = create_id()
        assert not result.endswith('\n')
    
    def test_create_id_generates_different_ids(self):
        """Test that create_id generates different IDs on multiple calls."""
        id1 = create_id()
        id2 = create_id()
        # Highly unlikely to be the same due to random component
        assert id1 != id2
    
    def test_create_id_multiple_calls(self):
        """Test that create_id can be called multiple times."""
        ids = [create_id() for _ in range(10)]
        assert len(ids) == 10
        # All should be strings
        assert all(isinstance(i, str) for i in ids)
        # All should be non-empty
        assert all(len(i) > 0 for i in ids)


class TestValue2Object:
    """Test the value2object function."""
    
    def test_value2object_with_literal(self):
        """Test that value2object returns Literal for Literal input."""
        lit = Literal("test")
        result = value2object(lit)
        assert result == lit
        assert isinstance(result, Literal)
    
    def test_value2object_with_uriref(self):
        """Test that value2object returns URIRef for URIRef input."""
        uri = URIRef("http://example.com/test")
        result = value2object(uri)
        assert result == uri
        assert isinstance(result, URIRef)
    
    def test_value2object_with_bnode(self):
        """Test that value2object returns BNode for BNode input."""
        bnode = BNode()
        result = value2object(bnode)
        assert result == bnode
        assert isinstance(result, BNode)
    
    def test_value2object_with_string(self):
        """Test that value2object converts string to Literal."""
        result = value2object("test string")
        assert isinstance(result, Literal)
        assert str(result) == "test string"
    
    def test_value2object_with_integer(self):
        """Test that value2object converts integer to Literal."""
        result = value2object(42)
        assert isinstance(result, Literal)
        assert result.value == 42
    
    def test_value2object_with_float(self):
        """Test that value2object converts float to Literal."""
        result = value2object(3.14)
        assert isinstance(result, Literal)
        assert result.value == 3.14
    
    def test_value2object_with_boolean(self):
        """Test that value2object converts boolean to Literal."""
        result = value2object(True)
        assert isinstance(result, Literal)
        assert result.value is True
    
    def test_value2object_with_none(self):
        """Test that value2object converts None to Literal."""
        result = value2object(None)
        assert isinstance(result, Literal)
    
    def test_value2object_returns_identifier_types(self):
        """Test that value2object returns Identifier types for RDF terms."""
        from rdflib.term import Identifier
        
        # Test with various RDF terms
        terms = [
            Literal("test"),
            URIRef("http://example.com"),
            BNode()
        ]
        
        for term in terms:
            result = value2object(term)
            assert isinstance(result, Identifier)
    
    def test_value2object_with_empty_string(self):
        """Test that value2object handles empty string."""
        result = value2object("")
        assert isinstance(result, Literal)
        assert str(result) == ""
    
    def test_value2object_with_unicode(self):
        """Test that value2object handles unicode strings."""
        result = value2object("Hello 世界")
        assert isinstance(result, Literal)
        assert str(result) == "Hello 世界"
    
    def test_value2object_with_zero(self):
        """Test that value2object handles zero."""
        result = value2object(0)
        assert isinstance(result, Literal)
        assert result.value == 0
    
    def test_value2object_preserves_datatype(self):
        """Test that value2object preserves typed literals."""
        from rdflib import XSD
        lit = Literal(42, datatype=XSD.integer)
        result = value2object(lit)
        assert result == lit
        assert result.datatype == XSD.integer
