"""
Unit tests for whyis.html_mime_types module.

Tests the HTML_MIME_TYPES set.
"""

import pytest
from whyis.html_mime_types import HTML_MIME_TYPES


class TestHTMLMimeTypes:
    """Test the HTML_MIME_TYPES set."""
    
    def test_html_mime_types_exists(self):
        """Test that HTML_MIME_TYPES is defined."""
        assert HTML_MIME_TYPES is not None
        assert isinstance(HTML_MIME_TYPES, set)
    
    def test_html_mime_types_not_empty(self):
        """Test that HTML_MIME_TYPES is not empty."""
        assert len(HTML_MIME_TYPES) > 0
    
    def test_text_html_present(self):
        """Test that text/html is in HTML_MIME_TYPES."""
        assert 'text/html' in HTML_MIME_TYPES
    
    def test_application_xhtml_present(self):
        """Test that application/xhtml is in HTML_MIME_TYPES."""
        assert 'application/xhtml' in HTML_MIME_TYPES
    
    def test_application_xhtml_xml_present(self):
        """Test that application/xhtml+xml is in HTML_MIME_TYPES."""
        assert 'application/xhtml+xml' in HTML_MIME_TYPES
    
    def test_html_mime_types_count(self):
        """Test that we have the expected number of HTML MIME types."""
        assert len(HTML_MIME_TYPES) == 3
    
    def test_all_entries_are_strings(self):
        """Test that all entries are strings."""
        for mime_type in HTML_MIME_TYPES:
            assert isinstance(mime_type, str), \
                f"MIME type {mime_type} should be a string"
    
    def test_no_duplicates(self):
        """Test that there are no duplicates (sets prevent this by nature)."""
        # Converting to list and back should give same size
        mime_list = list(HTML_MIME_TYPES)
        assert len(set(mime_list)) == len(mime_list)
    
    def test_mime_types_are_lowercase(self):
        """Test that MIME types are lowercase."""
        for mime_type in HTML_MIME_TYPES:
            assert mime_type == mime_type.lower(), \
                f"MIME type {mime_type} should be lowercase"
    
    def test_mime_types_format(self):
        """Test that MIME types follow the expected format."""
        for mime_type in HTML_MIME_TYPES:
            assert '/' in mime_type, \
                f"MIME type {mime_type} should contain a slash"
            parts = mime_type.split('/')
            assert len(parts) == 2, \
                f"MIME type {mime_type} should have exactly one slash"
            assert len(parts[0]) > 0 and len(parts[1]) > 0, \
                f"MIME type {mime_type} should have non-empty parts"
