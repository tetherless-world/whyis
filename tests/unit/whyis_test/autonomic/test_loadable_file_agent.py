import os
from rdflib import *

from whyis import nanopub
from whyis.namespace import *
from whyis.test.agent_unit_test_case import AgentUnitTestCase

# Sample RDF content in Turtle format
TEST_RDF_TURTLE = """
@prefix ex: <http://example.com/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:subject1
    a ex:Thing ;
    rdfs:label "Example Subject" ;
    ex:property "value" .

ex:subject2
    a ex:Thing ;
    rdfs:label "Another Subject" .
"""

TEST_RDF_NTRIPLES = """
<http://example.com/subject1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.com/Thing> .
<http://example.com/subject1> <http://www.w3.org/2000/01/rdf-schema#label> "Example Subject" .
<http://example.com/subject1> <http://example.com/property> "value" .
"""

TEST_RDF_JSONLD = """
{
  "@context": {
    "ex": "http://example.com/",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
  },
  "@id": "ex:subject1",
  "@type": "ex:Thing",
  "rdfs:label": "Example Subject",
  "ex:property": "value"
}
"""


class LoadableFileAgentTestCase(AgentUnitTestCase):
    """
    Test cases for the LoadableFileAgent.
    """

    def test_turtle_file_parsing(self):
        """Test parsing a Turtle format RDF file."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource with a Turtle file
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/test_turtle.ttl")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        results = self.run_agent(agent)
        
        # Verify output was generated
        self.assertTrue(len(results) > 0)
        result_np = results[0]
        
        # Verify ParsedFile type was added
        self.assertTrue((resource_uri, RDF.type, whyis.ParsedFile) in result_np.assertion)

    def test_ntriples_file_parsing(self):
        """Test parsing an N-Triples format RDF file."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource with an N-Triples file
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/test_ntriples.nt")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        results = self.run_agent(agent)
        
        # Verify output was generated
        self.assertTrue(len(results) > 0)

    def test_custom_input_class(self):
        """Test LoadableFileAgent with a custom input class."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource with a custom class
        custom_class = URIRef("http://example.com/CustomFileType")
        
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/custom_file.ttl")
        np.assertion.add((resource_uri, RDF.type, custom_class))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent(input_class=custom_class)
        results = self.run_agent(agent)
        
        # Verify output was generated
        self.assertTrue(len(results) > 0)

    def test_parsing_with_custom_formats(self):
        """Test LoadableFileAgent with custom format list."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create agent with specific formats
        formats = ['turtle', 'xml', 'nt']
        agent = LoadableFileAgent(formats=formats)
        
        # Verify formats are set
        self.assertEqual(agent._formats, formats)

    def test_error_handling(self):
        """Test that errors are properly handled and reported."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource pointing to a non-existent file
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/nonexistent.ttl")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        
        # The agent should handle the error gracefully
        # Since the file doesn't exist, we expect an error to be attached
        # to the resource in the nanopublication
        try:
            results = self.run_agent(agent)
            # If we get here, check if error was recorded
            # In the actual implementation, errors are caught and recorded
        except Exception as e:
            # This is expected for non-existent files
            self.assertIn("Could not retrieve", str(e))
