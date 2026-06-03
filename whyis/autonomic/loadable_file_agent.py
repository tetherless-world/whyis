from builtins import str
import rdflib
from datetime import datetime
import logging
import requests

from .update_change_service import UpdateChangeService
from whyis.nanopub import Nanopublication
from whyis.datastore import create_id
import flask
from depot.io.interfaces import StoredFile

from whyis.namespace import whyis, prov, sio


class LoadableFileAgent(UpdateChangeService):
    """
    An agent that parses files with RDF graph-aware formats and publishes
    them as nanopublications using the nanopublication manager.
    
    This agent supports:
    - Resources with a specific type (configurable, default: whyis:LoadableFile)
    - Both locally stored files (via whyis:hasFileID) and external URLs
    - Multiple RDF formats (auto-detection with fallback)
    - Error reporting when files cannot be parsed
    """
    
    activity_class = whyis.FileImport
    
    # RDF formats to try in order of likelihood
    RDF_FORMATS = [
        'turtle',    # Most likely for RDF files
        'xml',       # RDF/XML format
        'trig',      # TriG format for named graphs
        'n3',        # N3 notation
        'nquads',    # N-Quads for named quads
        'nt',        # N-Triples format
        'json-ld',   # JSON-LD format
        'hturtle',   # HTML with embedded RDF
        'trix',      # TriX XML format
        'rdfa',      # RDFa format
    ]
    
    def __init__(self, input_class=None, formats=None):
        """
        Initialize the LoadableFileAgent.
        
        Args:
            input_class: RDF class to process (default: whyis:LoadableFile)
            formats: List of RDF formats to try (default: RDF_FORMATS)
        """
        super(LoadableFileAgent, self).__init__()
        self._input_class = input_class
        self._formats = formats if formats is not None else self.RDF_FORMATS
    
    def getInputClass(self):
        """Return the class of resources to process."""
        if self._input_class is not None:
            return self._input_class
        return whyis.LoadableFile
    
    def getOutputClass(self):
        """Return the output class for processed resources."""
        return whyis.ParsedFile
    
    def get_query(self):
        """Return a SPARQL query to find resources to process."""
        return '''select ?resource where {
    ?resource rdf:type/rdfs:subClassOf* %s.
    filter not exists { ?resource rdf:type/rdfs:subClassOf* %s. }
}''' % (self.getInputClass().n3(), self.getOutputClass().n3())
    
    def process_nanopub(self, i, o, npub):
        """
        Process a LoadableFile resource by parsing its content and publishing
        the resulting RDF graph as nanopublications.
        
        Args:
            i: Input resource (the LoadableFile)
            o: Output resource (in the output nanopublication)
            npub: The nanopublication to add output to
        """
        logging.info("Processing LoadableFile: %s" % i.identifier)
        
        # Mark the output resource as a ParsedFile
        o.add(rdflib.RDF.type, self.getOutputClass())
        
        # Try to get the file content
        file_content = self._get_file_content(i.identifier)
        if file_content is None:
            raise Exception("Could not retrieve file content for %s" % i.identifier)
        
        # Try to parse the file in various formats
        parsed_graph = self._parse_file(file_content, i.identifier)
        
        if parsed_graph is None:
            raise Exception("Could not parse file %s in any supported RDF format" % i.identifier)
        
        # Add the parsed content to the assertion graph
        for s, p, obj in parsed_graph:
            npub.assertion.add((s, p, obj))
        
        # Add provenance information
        npub.pubinfo.add((npub.assertion.identifier, prov.wasQuotedFrom, i.identifier))
        npub.add((npub.identifier, sio.isAbout, i.identifier))
        npub.add((o.identifier, prov.wasDerivedFrom, i.identifier))
        
        logging.debug("Successfully parsed %d triples from %s" % (len(parsed_graph), i.identifier))
    
    def _get_file_content(self, resource_uri):
        """
        Retrieve file content from either a local file (via hasFileID) or
        a remote URL.
        
        Args:
            resource_uri: The URI of the resource
            
        Returns:
            File content as string or bytes, or None if retrieval fails
        """
        resource = self.app.get_resource(resource_uri)
        
        # Check for locally stored file via hasFileID
        fileid = resource.value(self.app.NS.whyis.hasFileID)
        if fileid is not None:
            try:
                stored_file = self.app.file_depot.get(fileid.value)
                if hasattr(stored_file, 'read'):
                    content = stored_file.read()
                else:
                    # If it's already file-like or string
                    content = stored_file
                # Handle both bytes and string
                if isinstance(content, bytes):
                    return content.decode('utf-8', errors='replace')
                return content
            except Exception as e:
                logging.error("Error reading local file %s: %s" % (fileid.value, str(e)))
                return None
        
        # Try to fetch from remote URL
        try:
            response = requests.get(str(resource_uri), timeout=30)
            response.raise_for_status()
            content = response.text
            return content
        except Exception as e:
            logging.error("Error fetching remote file from %s: %s" % (resource_uri, str(e)))
            return None
    
    def _parse_file(self, content, resource_uri):
        """
        Attempt to parse file content as RDF in various formats.
        
        Args:
            content: File content as string
            resource_uri: The URI to use as base for relative references
            
        Returns:
            Parsed RDF graph, or None if all formats fail
        """
        # Try the first guess based on file extension
        guessed_format = rdflib.util.guess_format(str(resource_uri))
        if guessed_format:
            result = self._try_parse_format(content, guessed_format, resource_uri)
            if result is not None:
                logging.debug("Successfully parsed as %s" % guessed_format)
                return result
        
        # Try all formats in order
        for fmt in self._formats:
            result = self._try_parse_format(content, fmt, resource_uri)
            if result is not None:
                logging.debug("Successfully parsed as %s" % fmt)
                return result
        
        return None
    
    def _try_parse_format(self, content, format_name, resource_uri):
        """
        Try to parse content in a specific RDF format.
        
        Args:
            content: File content as string
            format_name: The RDF format to try (e.g., 'turtle', 'xml')
            resource_uri: The URI to use as base for relative references
            
        Returns:
            Parsed graph if successful, None if parsing fails
        """
        try:
            g = rdflib.Graph()
            g.parse(data=content, format=format_name, publicID=str(resource_uri))
            return g
        except Exception as e:
            logging.debug("Could not parse as %s: %s" % (format_name, str(e)))
            return None
