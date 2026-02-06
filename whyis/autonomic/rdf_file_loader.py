"""
RDF File Loader Agent

This agent looks for resources of type whyis:RDFFile and loads them into the 
knowledge graph via the nanopublication_manager. It attaches appropriate 
provenance so that if the type designation is removed, the resulting graphs 
are also retired.

Supports:
1. Local files in the file depot (via whyis:hasFileID)
2. Remote files via HTTP/HTTPS
3. S3 URIs (via boto3, optional dependency)
"""

from builtins import str
import sadi
import rdflib
import logging
import tempfile
import requests
import os

from .update_change_service import UpdateChangeService
from whyis.nanopub import Nanopublication
import flask

from whyis.namespace import *

logger = logging.getLogger(__name__)


class RDFFileLoader(UpdateChangeService):
    """
    Agent that loads RDF files into the knowledge graph as nanopublications.
    
    This agent processes resources typed as whyis:RDFFile and loads their 
    content into the graph. It supports local files (via file depot), 
    HTTP/HTTPS URLs, and S3 URIs (when boto3 is available).
    """
    
    activity_class = whyis.RDFFileLoadingActivity
    
    def getInputClass(self):
        """Resources of type whyis:RDFFile that haven't been loaded yet."""
        return whyis.RDFFile
    
    def getOutputClass(self):
        """Marks resources as whyis:LoadedRDFFile after processing."""
        return whyis.LoadedRDFFile
    
    def get_query(self):
        """
        Query to find RDF files that need to be loaded.
        
        Only selects files that are typed as RDFFile but not yet LoadedRDFFile.
        """
        return '''select distinct ?resource where {
            ?resource a %s.
            filter not exists { ?resource a %s. }
        }''' % (self.getInputClass().n3(), self.getOutputClass().n3())
    
    def _load_from_file_depot(self, resource_uri, fileid):
        """
        Load RDF file from the local file depot.
        
        Args:
            resource_uri: URI of the resource
            fileid: File depot ID
            
        Returns:
            rdflib.Graph with loaded content, or None if loading fails
        """
        try:
            logger.info(f"Loading RDF file from depot: {resource_uri} (fileid: {fileid})")
            stored_file = flask.current_app.file_depot.get(fileid)
            
            # Create a temporary graph to load the file
            graph = rdflib.Graph()
            
            # Determine format from content type or file extension
            content_type = getattr(stored_file, 'content_type', None)
            format = self._guess_format(stored_file.name if hasattr(stored_file, 'name') else None, 
                                       content_type)
            
            # Read and parse the file
            with stored_file as f:
                content = f.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                graph.parse(data=content, format=format)
            
            logger.info(f"Successfully loaded {len(graph)} triples from file depot")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load RDF from file depot {fileid}: {e}")
            raise
    
    def _load_from_http(self, url):
        """
        Load RDF file from HTTP/HTTPS URL.
        
        Args:
            url: HTTP/HTTPS URL to fetch
            
        Returns:
            rdflib.Graph with loaded content, or None if loading fails
        """
        try:
            logger.info(f"Loading RDF file from HTTP: {url}")
            response = requests.get(url, headers={'Accept': 'application/rdf+xml, text/turtle, application/n-triples, application/ld+json'})
            response.raise_for_status()
            
            graph = rdflib.Graph()
            
            # Determine format from content type or URL
            content_type = response.headers.get('content-type', '').split(';')[0].strip()
            format = self._guess_format(url, content_type)
            
            graph.parse(data=response.text, format=format)
            
            logger.info(f"Successfully loaded {len(graph)} triples from HTTP")
            return graph
            
        except Exception as e:
            logger.error(f"Failed to load RDF from HTTP {url}: {e}")
            raise
    
    def _load_from_s3(self, s3_uri):
        """
        Load RDF file from S3 URI.
        
        Args:
            s3_uri: S3 URI (s3://bucket/key)
            
        Returns:
            rdflib.Graph with loaded content, or None if loading fails
        """
        try:
            import boto3
        except ImportError:
            error_msg = "boto3 is not installed. Cannot load from S3. Install with: pip install boto3"
            logger.error(error_msg)
            raise ImportError(error_msg)
        
        try:
            logger.info(f"Loading RDF file from S3: {s3_uri}")
            
            # Parse S3 URI: s3://bucket/key
            if not s3_uri.startswith('s3://'):
                raise ValueError(f"Invalid S3 URI: {s3_uri}")
            
            parts = s3_uri[5:].split('/', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid S3 URI format: {s3_uri}")
            
            bucket_name, key = parts
            
            # Use default credentials (from environment, config, or IAM role)
            s3_client = boto3.client('s3')
            
            # Download file to temporary location
            tmp_file = None
            try:
                tmp_file = tempfile.NamedTemporaryFile(mode='w+b', delete=False)
                tmp_path = tmp_file.name
                tmp_file.close()  # Close so boto3 can write to it
                
                s3_client.download_file(bucket_name, key, tmp_path)
                
                # Parse the file
                graph = rdflib.Graph()
                format = self._guess_format(key, None)
                graph.parse(tmp_path, format=format)
                
                logger.info(f"Successfully loaded {len(graph)} triples from S3")
                return graph
                
            finally:
                # Clean up temp file in all cases
                if tmp_file is not None and os.path.exists(tmp_path):
                    os.unlink(tmp_path)
            
        except Exception as e:
            logger.error(f"Failed to load RDF from S3 {s3_uri}: {e}")
            raise
    
    def _guess_format(self, filename, content_type):
        """
        Guess RDF format from filename or content type.
        
        Args:
            filename: Filename or URL
            content_type: MIME type
            
        Returns:
            Format string for rdflib (e.g., 'turtle', 'xml', 'json-ld')
        """
        # First try content type
        if content_type:
            content_type = content_type.lower()
            if 'turtle' in content_type or content_type == 'text/turtle':
                return 'turtle'
            elif 'rdf+xml' in content_type or content_type == 'application/rdf+xml':
                return 'xml'
            elif 'n-triples' in content_type or content_type == 'application/n-triples':
                return 'nt'
            elif 'n3' in content_type or content_type == 'text/n3':
                return 'n3'
            elif 'ld+json' in content_type or content_type == 'application/ld+json':
                return 'json-ld'
            elif 'trig' in content_type or content_type == 'application/trig':
                return 'trig'
        
        # Fall back to file extension
        if filename:
            filename = filename.lower()
            if filename.endswith('.ttl') or filename.endswith('.turtle'):
                return 'turtle'
            elif filename.endswith('.rdf') or filename.endswith('.owl') or filename.endswith('.xml'):
                return 'xml'
            elif filename.endswith('.nt'):
                return 'nt'
            elif filename.endswith('.n3'):
                return 'n3'
            elif filename.endswith('.jsonld') or filename.endswith('.json-ld'):
                return 'json-ld'
            elif filename.endswith('.trig'):
                return 'trig'
            elif filename.endswith('.nq'):
                return 'nquads'
        
        # Default to turtle
        return 'turtle'
    
    def process(self, i, o):
        """
        Process an RDF file resource and load its content into the graph.
        
        Args:
            i: Input resource (typed as whyis:RDFFile)
            o: Output resource (to be marked as whyis:LoadedRDFFile)
        """
        resource_uri = i.identifier
        logger.info(f"Processing RDF file: {resource_uri}")
        
        # Check if this is a local file in the depot
        fileid = i.value(flask.current_app.NS.whyis.hasFileID)
        
        graph = None
        
        if fileid is not None:
            # Local file in depot
            logger.info(f"Found local file in depot: {fileid.value}")
            graph = self._load_from_file_depot(resource_uri, fileid.value)
            
        elif str(resource_uri).startswith('http://') or str(resource_uri).startswith('https://'):
            # HTTP/HTTPS URL
            graph = self._load_from_http(str(resource_uri))
            
        elif str(resource_uri).startswith('s3://'):
            # S3 URI
            graph = self._load_from_s3(str(resource_uri))
            
        else:
            error_msg = f"Cannot determine how to load RDF file: {resource_uri}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if graph is None or len(graph) == 0:
            logger.warning(f"No triples loaded from {resource_uri}")
            return
        
        # Add the loaded graph to the output nanopub
        # The triples will be published as part of the agent's normal flow
        for s, p, o_triple in graph:
            o.graph.add((s, p, o_triple))
        
        logger.info(f"Successfully loaded {len(graph)} triples from {resource_uri}")
