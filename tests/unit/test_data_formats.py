"""
Unit tests for whyis.data_formats module.

Tests the DATA_FORMATS dictionary mappings.
"""

import pytest
from whyis.data_formats import DATA_FORMATS


class TestDataFormats:
    """Test the DATA_FORMATS dictionary."""
    
    def test_data_formats_exists(self):
        """Test that DATA_FORMATS is defined."""
        assert DATA_FORMATS is not None
        assert isinstance(DATA_FORMATS, dict)
    
    def test_rdf_xml_format(self):
        """Test RDF/XML MIME type mapping."""
        assert DATA_FORMATS["application/rdf+xml"] == "xml"
    
    def test_json_ld_format(self):
        """Test JSON-LD MIME type mapping."""
        assert DATA_FORMATS["application/ld+json"] == "json-ld"
    
    def test_json_format_as_json_ld(self):
        """Test that application/json maps to json-ld."""
        assert DATA_FORMATS["application/json"] == "json-ld"
    
    def test_turtle_format(self):
        """Test Turtle MIME type mapping."""
        assert DATA_FORMATS["text/turtle"] == "turtle"
    
    def test_trig_format(self):
        """Test TriG MIME type mapping."""
        assert DATA_FORMATS["application/trig"] == "trig"
    
    def test_nquads_format(self):
        """Test N-Quads MIME type mapping."""
        assert DATA_FORMATS["application/n-quads"] == "nquads"
    
    def test_ntriples_format(self):
        """Test N-Triples MIME type mapping."""
        assert DATA_FORMATS["application/n-triples"] == "nt"
    
    def test_rdf_json_format(self):
        """Test RDF/JSON MIME type mapping."""
        assert DATA_FORMATS["application/rdf+json"] == "json"
    
    def test_html_format_is_none(self):
        """Test that HTML MIME type maps to None."""
        assert DATA_FORMATS["text/html"] is None
    
    def test_xhtml_xml_format_is_none(self):
        """Test that XHTML+XML MIME type maps to None."""
        assert DATA_FORMATS["application/xhtml+xml"] is None
    
    def test_xhtml_format_is_none(self):
        """Test that XHTML MIME type maps to None."""
        assert DATA_FORMATS["application/xhtml"] is None
    
    def test_none_key_default(self):
        """Test that None key maps to default json-ld."""
        assert DATA_FORMATS[None] == "json-ld"
    
    def test_all_rdf_formats_are_strings_or_none(self):
        """Test that all format values are strings or None."""
        for mime_type, format_name in DATA_FORMATS.items():
            assert format_name is None or isinstance(format_name, str), \
                f"Format for {mime_type} should be string or None, got {type(format_name)}"
    
    def test_rdf_serialization_formats_count(self):
        """Test that we have expected number of format mappings."""
        # We should have at least the basic RDF serialization formats
        rdf_formats = [v for v in DATA_FORMATS.values() if v is not None]
        assert len(rdf_formats) >= 7  # xml, json-ld, turtle, trig, nquads, nt, json
    
    def test_common_mime_types_present(self):
        """Test that common RDF MIME types are present."""
        common_types = [
            "application/rdf+xml",
            "text/turtle",
            "application/ld+json",
            "application/trig"
        ]
        for mime_type in common_types:
            assert mime_type in DATA_FORMATS, f"{mime_type} should be in DATA_FORMATS"
    
    def test_mime_types_are_lowercase(self):
        """Test that MIME types are properly lowercase (except None)."""
        for mime_type in DATA_FORMATS.keys():
            if mime_type is not None:
                assert mime_type == mime_type.lower(), \
                    f"MIME type {mime_type} should be lowercase"
