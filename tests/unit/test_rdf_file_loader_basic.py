"""
Simple unit tests for RDFFileLoader agent that don't require full app context.

Tests basic functionality like format guessing and URI parsing.
"""

import pytest
from unittest.mock import Mock, patch
from rdflib import URIRef

from whyis.autonomic.rdf_file_loader import RDFFileLoader
from whyis.namespace import whyis


class TestRDFFileLoaderBasic:
    """Basic tests for RDFFileLoader that don't require app context."""
    
    def test_agent_initialization(self):
        """Test that RDFFileLoader agent can be initialized."""
        agent = RDFFileLoader()
        assert agent is not None
        assert hasattr(agent, 'activity_class')
        assert agent.activity_class == whyis.RDFFileLoadingActivity
    
    def test_agent_input_class(self):
        """Test that RDFFileLoader returns correct input class."""
        agent = RDFFileLoader()
        input_class = agent.getInputClass()
        assert input_class == whyis.RDFFile
    
    def test_agent_output_class(self):
        """Test that RDFFileLoader returns correct output class."""
        agent = RDFFileLoader()
        output_class = agent.getOutputClass()
        assert output_class == whyis.LoadedRDFFile
    
    def test_agent_has_query(self):
        """Test that RDFFileLoader has get_query method."""
        agent = RDFFileLoader()
        assert hasattr(agent, 'get_query')
        assert callable(agent.get_query)
        query = agent.get_query()
        assert 'RDFFile' in query
        assert 'LoadedRDFFile' in query
    
    def test_format_guessing_turtle(self):
        """Test RDF format guessing for Turtle files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.ttl', None) == 'turtle'
        assert agent._guess_format('test.turtle', None) == 'turtle'
        
        # Test by content type
        assert agent._guess_format(None, 'text/turtle') == 'turtle'
        assert agent._guess_format('file.dat', 'text/turtle') == 'turtle'
    
    def test_format_guessing_rdfxml(self):
        """Test RDF format guessing for RDF/XML files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.rdf', None) == 'xml'
        assert agent._guess_format('test.owl', None) == 'xml'
        assert agent._guess_format('test.xml', None) == 'xml'
        
        # Test by content type
        assert agent._guess_format(None, 'application/rdf+xml') == 'xml'
    
    def test_format_guessing_jsonld(self):
        """Test RDF format guessing for JSON-LD files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.jsonld', None) == 'json-ld'
        assert agent._guess_format('test.json-ld', None) == 'json-ld'
        
        # Test by content type
        assert agent._guess_format(None, 'application/ld+json') == 'json-ld'
    
    def test_format_guessing_ntriples(self):
        """Test RDF format guessing for N-Triples files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.nt', None) == 'nt'
        
        # Test by content type
        assert agent._guess_format(None, 'application/n-triples') == 'nt'
    
    def test_format_guessing_n3(self):
        """Test RDF format guessing for N3 files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.n3', None) == 'n3'
        
        # Test by content type
        assert agent._guess_format(None, 'text/n3') == 'n3'
    
    def test_format_guessing_trig(self):
        """Test RDF format guessing for TriG files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.trig', None) == 'trig'
        
        # Test by content type
        assert agent._guess_format(None, 'application/trig') == 'trig'
    
    def test_format_guessing_nquads(self):
        """Test RDF format guessing for N-Quads files."""
        agent = RDFFileLoader()
        
        # Test by filename
        assert agent._guess_format('test.nq', None) == 'nquads'
    
    def test_format_guessing_default(self):
        """Test that format guessing defaults to turtle."""
        agent = RDFFileLoader()
        
        # No filename or content type
        assert agent._guess_format(None, None) == 'turtle'
        
        # Unknown extension
        assert agent._guess_format('test.unknown', None) == 'turtle'
        
        # Unknown content type
        assert agent._guess_format(None, 'application/unknown') == 'turtle'
    
    def test_load_from_s3_without_boto3(self):
        """Test that loading from S3 fails gracefully when boto3 is not installed."""
        agent = RDFFileLoader()
        
        # Mock boto3 import to fail by patching it in the function
        with patch.dict('sys.modules', {'boto3': None}):
            with pytest.raises(ImportError) as exc_info:
                agent._load_from_s3('s3://bucket/key.ttl')
            
            assert 'boto3' in str(exc_info.value).lower()
    
    def test_load_from_s3_invalid_uri(self):
        """Test that invalid S3 URIs are rejected."""
        agent = RDFFileLoader()
        
        # Mock boto3 module
        mock_boto3_module = Mock()
        mock_s3_client = Mock()
        mock_boto3_module.client.return_value = mock_s3_client
        
        with patch.dict('sys.modules', {'boto3': mock_boto3_module}):
            # Invalid URI (no bucket/key)
            with pytest.raises(ValueError) as exc_info:
                agent._load_from_s3('s3://bucket-only')
            assert 'Invalid S3 URI' in str(exc_info.value)
            
            # Invalid URI (not s3://)
            with pytest.raises(ValueError) as exc_info:
                agent._load_from_s3('http://not-s3.com/file.ttl')
            assert 'Invalid S3 URI' in str(exc_info.value)
