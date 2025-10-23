"""
Unit tests for whyis.blueprint.nanopub.nanopub_utils module.

Tests utility constants and simple functions for nanopublication handling.
"""

import pytest


class TestNanopubUtils:
    """Test nanopub utility constants."""
    
    def test_graph_aware_formats_exists(self):
        """Test that graph_aware_formats is defined."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        assert graph_aware_formats is not None
    
    def test_graph_aware_formats_is_set(self):
        """Test that graph_aware_formats is a set."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        assert isinstance(graph_aware_formats, set)
    
    def test_graph_aware_formats_not_empty(self):
        """Test that graph_aware_formats is not empty."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        assert len(graph_aware_formats) > 0
    
    def test_graph_aware_formats_contains_jsonld(self):
        """Test that graph_aware_formats contains json-ld."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        assert "json-ld" in graph_aware_formats
    
    def test_graph_aware_formats_contains_trig(self):
        """Test that graph_aware_formats contains trig."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        assert "trig" in graph_aware_formats
    
    def test_graph_aware_formats_contains_nquads(self):
        """Test that graph_aware_formats contains nquads."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        assert "nquads" in graph_aware_formats
    
    def test_graph_aware_formats_count(self):
        """Test the number of graph-aware formats."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        # Should have at least these 3 formats
        assert len(graph_aware_formats) >= 3
    
    def test_graph_aware_formats_all_strings(self):
        """Test that all formats are strings."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        for fmt in graph_aware_formats:
            assert isinstance(fmt, str)
    
    def test_graph_aware_formats_lowercase(self):
        """Test that all formats are lowercase."""
        from whyis.blueprint.nanopub.nanopub_utils import graph_aware_formats
        
        for fmt in graph_aware_formats:
            assert fmt == fmt.lower()
    
    def test_get_nanopub_uri_function_exists(self):
        """Test that get_nanopub_uri function exists."""
        from whyis.blueprint.nanopub import nanopub_utils
        
        assert hasattr(nanopub_utils, 'get_nanopub_uri')
        assert callable(nanopub_utils.get_nanopub_uri)
    
    def test_load_nanopub_graph_function_exists(self):
        """Test that load_nanopub_graph function exists."""
        from whyis.blueprint.nanopub import nanopub_utils
        
        assert hasattr(nanopub_utils, 'load_nanopub_graph')
        assert callable(nanopub_utils.load_nanopub_graph)
    
    def test_get_nanopub_graph_function_exists(self):
        """Test that get_nanopub_graph function exists."""
        from whyis.blueprint.nanopub import nanopub_utils
        
        assert hasattr(nanopub_utils, 'get_nanopub_graph')
        assert callable(nanopub_utils.get_nanopub_graph)
    
    def test_prep_nanopub_function_exists(self):
        """Test that prep_nanopub function exists."""
        from whyis.blueprint.nanopub import nanopub_utils
        
        assert hasattr(nanopub_utils, 'prep_nanopub')
        assert callable(nanopub_utils.prep_nanopub)
