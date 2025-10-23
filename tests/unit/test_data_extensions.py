"""
Unit tests for whyis.data_extensions module.

Tests the DATA_EXTENSIONS dictionary mappings.
"""

import pytest
from whyis.data_extensions import DATA_EXTENSIONS


class TestDataExtensions:
    """Test the DATA_EXTENSIONS dictionary."""
    
    def test_data_extensions_exists(self):
        """Test that DATA_EXTENSIONS is defined."""
        assert DATA_EXTENSIONS is not None
        assert isinstance(DATA_EXTENSIONS, dict)
    
    def test_data_extensions_not_empty(self):
        """Test that DATA_EXTENSIONS is not empty."""
        assert len(DATA_EXTENSIONS) > 0
    
    def test_rdf_extension(self):
        """Test RDF extension mapping."""
        assert DATA_EXTENSIONS["rdf"] == "application/rdf+xml"
    
    def test_jsonld_extension(self):
        """Test JSON-LD extension mapping."""
        assert DATA_EXTENSIONS["jsonld"] == "application/ld+json"
    
    def test_json_extension(self):
        """Test JSON extension mapping."""
        assert DATA_EXTENSIONS["json"] == "application/json"
    
    def test_ttl_extension(self):
        """Test TTL extension mapping."""
        assert DATA_EXTENSIONS["ttl"] == "text/turtle"
    
    def test_turtle_extension(self):
        """Test turtle extension mapping."""
        assert DATA_EXTENSIONS["turtle"] == "text/turtle"
    
    def test_trig_extension(self):
        """Test TriG extension mapping."""
        assert DATA_EXTENSIONS["trig"] == "application/trig"
    
    def test_owl_extension(self):
        """Test OWL extension mapping."""
        assert DATA_EXTENSIONS["owl"] == "application/rdf+xml"
    
    def test_nq_extension(self):
        """Test N-Quads extension mapping."""
        assert DATA_EXTENSIONS["nq"] == "application/n-quads"
    
    def test_nt_extension(self):
        """Test N-Triples extension mapping."""
        assert DATA_EXTENSIONS["nt"] == "application/n-triples"
    
    def test_html_extension(self):
        """Test HTML extension mapping."""
        assert DATA_EXTENSIONS["html"] == "text/html"
    
    def test_all_extensions_are_strings(self):
        """Test that all extensions are strings."""
        for ext in DATA_EXTENSIONS.keys():
            assert isinstance(ext, str), \
                f"Extension {ext} should be a string"
    
    def test_all_mime_types_are_strings(self):
        """Test that all MIME types are strings."""
        for mime_type in DATA_EXTENSIONS.values():
            assert isinstance(mime_type, str), \
                f"MIME type {mime_type} should be a string"
    
    def test_extensions_are_lowercase(self):
        """Test that all extensions are lowercase."""
        for ext in DATA_EXTENSIONS.keys():
            assert ext == ext.lower(), \
                f"Extension {ext} should be lowercase"
    
    def test_mime_types_are_lowercase(self):
        """Test that all MIME types are lowercase."""
        for mime_type in DATA_EXTENSIONS.values():
            assert mime_type == mime_type.lower(), \
                f"MIME type {mime_type} should be lowercase"
    
    def test_common_rdf_extensions_present(self):
        """Test that common RDF extensions are present."""
        common_extensions = ["rdf", "ttl", "jsonld", "owl", "nt"]
        for ext in common_extensions:
            assert ext in DATA_EXTENSIONS, \
                f"Extension {ext} should be in DATA_EXTENSIONS"
    
    def test_turtle_and_ttl_same_mime_type(self):
        """Test that 'turtle' and 'ttl' map to the same MIME type."""
        assert DATA_EXTENSIONS["turtle"] == DATA_EXTENSIONS["ttl"]
    
    def test_rdf_and_owl_same_mime_type(self):
        """Test that 'rdf' and 'owl' map to the same MIME type (RDF/XML)."""
        assert DATA_EXTENSIONS["rdf"] == DATA_EXTENSIONS["owl"]
    
    def test_mime_types_contain_slash(self):
        """Test that all MIME types contain a slash."""
        for mime_type in DATA_EXTENSIONS.values():
            assert '/' in mime_type, \
                f"MIME type {mime_type} should contain a slash"
    
    def test_mime_types_format(self):
        """Test that MIME types follow the expected format."""
        for mime_type in DATA_EXTENSIONS.values():
            parts = mime_type.split('/')
            assert len(parts) == 2, \
                f"MIME type {mime_type} should have exactly one slash"
            assert len(parts[0]) > 0 and len(parts[1]) > 0, \
                f"MIME type {mime_type} should have non-empty parts"
    
    def test_extensions_have_no_dots(self):
        """Test that extensions don't include leading dots."""
        for ext in DATA_EXTENSIONS.keys():
            assert not ext.startswith('.'), \
                f"Extension {ext} should not start with a dot"
