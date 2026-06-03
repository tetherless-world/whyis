import os
from rdflib import URIRef, RDF, Graph
from unittest.mock import patch, MagicMock

from whyis import nanopub
from whyis.namespace import whyis, NS, prov, sio, sioc
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
  "@id": "http://example.com/subject1",
  "@type": "http://example.com/Thing",
  "http://www.w3.org/2000/01/rdf-schema#label": "Example Subject",
  "http://example.com/property": "value"
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
        
        # Create a resource and mock file content
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/test_turtle.ttl")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        
        # Mock the file retrieval to return test RDF content
        with patch.object(agent, '_get_file_content', return_value=TEST_RDF_TURTLE):
            results = self.run_agent(agent)
        
        # Verify output was generated
        self.assertTrue(len(results) > 0)
        result_np = results[0]
        
        # Verify ParsedFile type was added to the output resource
        # The output resource has the same identifier as the input resource
        self.assertTrue((resource_uri, RDF.type, whyis.ParsedFile) in result_np.assertion)
        
        # Verify RDF content was parsed (should have triples from the test RDF)
        self.assertTrue(len(result_np.assertion) > 1)

    def test_ntriples_file_parsing(self):
        """Test parsing an N-Triples format RDF file."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/test_ntriples.nt")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        
        # Mock the file retrieval to return test RDF content
        with patch.object(agent, '_get_file_content', return_value=TEST_RDF_NTRIPLES):
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
        
        # Mock the file retrieval to return test RDF content
        with patch.object(agent, '_get_file_content', return_value=TEST_RDF_TURTLE):
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

    def test_error_handling_missing_file(self):
        """Test that errors are properly handled for missing files."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource pointing to a non-existent file
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/nonexistent.ttl")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        
        # Mock the file retrieval to return None (file not found)
        with patch.object(agent, '_get_file_content', return_value=None):
            results = self.run_agent(agent)
        
        # Verify that an output was generated
        self.assertTrue(len(results) > 0)
        result_np = results[0]
        
        # Verify that an error message was recorded
        # The error should be in the assertion as sioc:content on the assertion identifier
        error_messages = list(result_np.assertion.objects(result_np.assertion.identifier, sioc.content))
        self.assertTrue(len(error_messages) > 0)
        self.assertIn("Could not retrieve", str(error_messages[0]))

    def test_error_handling_invalid_rdf(self):
        """Test that errors are properly handled for invalid RDF."""
        self.dry_run = False
        
        from whyis.autonomic import LoadableFileAgent
        
        # Create a resource
        np = nanopub.Nanopublication()
        resource_uri = URIRef("http://example.com/invalid.ttl")
        np.assertion.add((resource_uri, RDF.type, whyis.LoadableFile))
        
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        agent = LoadableFileAgent()
        
        # Mock the file retrieval to return invalid RDF content
        with patch.object(agent, '_get_file_content', return_value="This is not valid RDF content at all!!!"):
            results = self.run_agent(agent)
        
        # Verify that an output was generated
        self.assertTrue(len(results) > 0)
        result_np = results[0]
        
        # Verify that an error message was recorded
        error_messages = list(result_np.assertion.objects(result_np.assertion.identifier, sioc.content))
        self.assertTrue(len(error_messages) > 0)
        self.assertIn("Could not parse", str(error_messages[0]))
