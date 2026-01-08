"""
Integration tests for RDFFileLoader agent with mocked HTTP, S3, and file depot.

These tests use mocks to simulate HTTP requests, S3 access, and file depot operations
without requiring external dependencies or a full app context.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from rdflib import Graph, URIRef, RDF

from whyis.autonomic.rdf_file_loader import RDFFileLoader


# Test RDF data in Turtle format
test_rdf_turtle = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex:    <http://example.com/> .

ex:subject1 a ex:Class1 ;
    rdfs:label "Test Subject 1" ;
    ex:property "Test Value" .

ex:subject2 a ex:Class2 ;
    rdfs:label "Test Subject 2" ;
    ex:relatedTo ex:subject1 .
"""

# Test RDF data in RDF/XML format
test_rdf_xml = """<?xml version="1.0"?>
<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
         xmlns:ex="http://example.com/">
  <ex:Class1 rdf:about="http://example.com/subject1">
    <rdfs:label>Test Subject 1</rdfs:label>
    <ex:property>Test Value</ex:property>
  </ex:Class1>
</rdf:RDF>
"""


class TestRDFFileLoaderHTTP:
    """Tests for loading RDF files via HTTP/HTTPS."""
    
    def test_load_from_http_turtle(self):
        """Test loading RDF from HTTP URL with Turtle format."""
        agent = RDFFileLoader()
        
        # Mock requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_rdf_turtle
        mock_response.headers = {'content-type': 'text/turtle'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            graph = agent._load_from_http('http://example.com/data.ttl')
            
            # Verify
            assert graph is not None
            assert len(graph) > 0
            assert (URIRef('http://example.com/subject1'), 
                   RDF.type, 
                   URIRef('http://example.com/Class1')) in graph
    
    def test_load_from_https_rdfxml(self):
        """Test loading RDF from HTTPS URL with RDF/XML format."""
        agent = RDFFileLoader()
        
        # Mock requests.get
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_rdf_xml
        mock_response.headers = {'content-type': 'application/rdf+xml'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            graph = agent._load_from_http('https://example.com/data.rdf')
            
            # Verify
            assert graph is not None
            assert len(graph) > 0
            # Check that at least one triple was loaded
            assert len(list(graph.triples((None, None, None)))) > 0
    
    def test_load_from_http_with_content_negotiation(self):
        """Test that HTTP requests include proper Accept headers."""
        agent = RDFFileLoader()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = test_rdf_turtle
        mock_response.headers = {'content-type': 'text/turtle'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response) as mock_get:
            graph = agent._load_from_http('http://example.com/data')
            
            # Verify that requests.get was called with Accept headers
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert 'headers' in call_args[1]
            assert 'Accept' in call_args[1]['headers']
    
    def test_load_from_http_error_handling(self):
        """Test error handling for HTTP failures."""
        agent = RDFFileLoader()
        
        # Mock a failed HTTP request
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                agent._load_from_http('http://example.com/nonexistent.ttl')


class TestRDFFileLoaderS3:
    """Tests for loading RDF files from S3."""
    
    def test_load_from_s3_success(self):
        """Test successful loading from S3."""
        agent = RDFFileLoader()
        
        # Create mock boto3 module and client
        mock_s3_client = Mock()
        mock_boto3_module = Mock()
        mock_boto3_module.client.return_value = mock_s3_client
        
        # Mock file download
        call_count = {'count': 0}
        def mock_download(bucket, key, fileobj):
            call_count['count'] += 1
            fileobj.write(test_rdf_turtle.encode('utf-8'))
        
        mock_s3_client.download_fileobj = mock_download
        
        with patch.dict('sys.modules', {'boto3': mock_boto3_module}):
            graph = agent._load_from_s3('s3://test-bucket/data.ttl')
            
            # Verify
            assert graph is not None
            assert len(graph) > 0
            assert (URIRef('http://example.com/subject1'), 
                   RDF.type, 
                   URIRef('http://example.com/Class1')) in graph
            
            # Verify boto3 was called correctly
            mock_boto3_module.client.assert_called_once_with('s3')
            assert call_count['count'] == 1
    
    def test_load_from_s3_uri_parsing(self):
        """Test that S3 URIs are correctly parsed."""
        agent = RDFFileLoader()
        
        mock_s3_client = Mock()
        mock_boto3_module = Mock()
        mock_boto3_module.client.return_value = mock_s3_client
        
        def mock_download(bucket, key, fileobj):
            # Verify bucket and key are parsed correctly
            assert bucket == 'my-bucket'
            assert key == 'path/to/file.ttl'
            fileobj.write(test_rdf_turtle.encode('utf-8'))
        
        mock_s3_client.download_fileobj = mock_download
        
        with patch.dict('sys.modules', {'boto3': mock_boto3_module}):
            graph = agent._load_from_s3('s3://my-bucket/path/to/file.ttl')
            assert graph is not None
    
    def test_load_from_s3_with_format_detection(self):
        """Test that format is detected from S3 key extension."""
        agent = RDFFileLoader()
        
        mock_s3_client = Mock()
        mock_boto3_module = Mock()
        mock_boto3_module.client.return_value = mock_s3_client
        
        def mock_download(bucket, key, fileobj):
            fileobj.write(test_rdf_xml.encode('utf-8'))
        
        mock_s3_client.download_fileobj = mock_download
        
        with patch.dict('sys.modules', {'boto3': mock_boto3_module}):
            # Test with .rdf extension
            graph = agent._load_from_s3('s3://bucket/file.rdf')
            assert graph is not None
            assert len(graph) > 0


class TestRDFFileLoaderFileDepot:
    """Tests for loading RDF files from local file depot."""
    
    def test_load_from_file_depot_turtle(self):
        """Test loading RDF from file depot with Turtle format."""
        agent = RDFFileLoader()
        
        # Create a mock stored file
        mock_stored_file = Mock()
        mock_stored_file.name = 'test.ttl'
        mock_stored_file.content_type = 'text/turtle'
        mock_stored_file.read.return_value = test_rdf_turtle.encode('utf-8')
        mock_stored_file.__enter__ = Mock(return_value=mock_stored_file)
        mock_stored_file.__exit__ = Mock(return_value=None)
        
        # Mock flask.current_app.file_depot
        mock_app = Mock()
        mock_app.file_depot.get.return_value = mock_stored_file
        
        with patch('flask.current_app', mock_app):
            graph = agent._load_from_file_depot(
                URIRef('http://example.com/file1'),
                'test_fileid'
            )
            
            # Verify
            assert graph is not None
            assert len(graph) > 0
            assert (URIRef('http://example.com/subject1'), 
                   RDF.type, 
                   URIRef('http://example.com/Class1')) in graph
    
    def test_load_from_file_depot_format_detection(self):
        """Test format detection from file depot content type."""
        agent = RDFFileLoader()
        
        # Create a mock stored file with XML content
        mock_stored_file = Mock()
        mock_stored_file.name = 'test.dat'  # Ambiguous extension
        mock_stored_file.content_type = 'application/rdf+xml'  # Clear content type
        mock_stored_file.read.return_value = test_rdf_xml.encode('utf-8')
        mock_stored_file.__enter__ = Mock(return_value=mock_stored_file)
        mock_stored_file.__exit__ = Mock(return_value=None)
        
        mock_app = Mock()
        mock_app.file_depot.get.return_value = mock_stored_file
        
        with patch('flask.current_app', mock_app):
            graph = agent._load_from_file_depot(
                URIRef('http://example.com/file2'),
                'test_fileid_2'
            )
            
            # Verify
            assert graph is not None
            assert len(graph) > 0
    
    def test_load_from_file_depot_error_handling(self):
        """Test error handling when file depot access fails."""
        agent = RDFFileLoader()
        
        # Mock file depot to raise an error
        mock_app = Mock()
        mock_app.file_depot.get.side_effect = Exception("File not found in depot")
        
        with patch('flask.current_app', mock_app):
            with pytest.raises(Exception):
                agent._load_from_file_depot(
                    URIRef('http://example.com/file3'),
                    'nonexistent_fileid'
                )


class TestRDFFileLoaderErrorHandling:
    """Tests for error handling in RDF file loading."""
    
    def test_invalid_rdf_content(self):
        """Test handling of invalid RDF content."""
        agent = RDFFileLoader()
        
        # Mock HTTP response with invalid RDF
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "This is not valid RDF content"
        mock_response.headers = {'content-type': 'text/turtle'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            with pytest.raises(Exception):
                # Should fail to parse invalid RDF
                agent._load_from_http('http://example.com/invalid.ttl')
    
    def test_empty_graph(self):
        """Test handling of empty RDF files."""
        agent = RDFFileLoader()
        
        # Mock HTTP response with empty but valid RDF
        empty_rdf = "@prefix ex: <http://example.com/> ."
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = empty_rdf
        mock_response.headers = {'content-type': 'text/turtle'}
        mock_response.raise_for_status = Mock()
        
        with patch('requests.get', return_value=mock_response):
            graph = agent._load_from_http('http://example.com/empty.ttl')
            
            # Should succeed but return empty graph
            assert graph is not None
            assert len(graph) == 0
