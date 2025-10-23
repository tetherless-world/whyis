"""
Component tests for ImporterCrawler agent.

Tests the importer crawling functionality using the in-memory app infrastructure.
"""

import os
from rdflib import *

from whyis import nanopub
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase


test_importer_crawler_rdf = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix whyis: <http://vocab.rpi.edu/whyis/> .
@prefix :      <http://example.com/importer/> .

:resource1 a whyis:ImporterResource ;
    rdfs:label "Resource to crawl" ;
    :linkedTo :resource2 .

:resource2 a rdfs:Resource ;
    rdfs:label "Linked resource" .
"""


class ImporterCrawlerTestCase(AgentUnitTestCase):
    """Test the ImporterCrawler agent functionality."""
    
    def test_importer_crawler_initialization(self):
        """Test that ImporterCrawler agent can be initialized."""
        agent = autonomic.ImporterCrawler()
        assert agent is not None
        assert hasattr(agent, 'activity_class')
    
    def test_importer_crawler_input_class(self):
        """Test that ImporterCrawler returns correct input class."""
        agent = autonomic.ImporterCrawler()
        input_class = agent.getInputClass()
        assert input_class == NS.whyis.ImporterResource
    
    def test_importer_crawler_output_class(self):
        """Test that ImporterCrawler returns correct output class."""
        agent = autonomic.ImporterCrawler()
        output_class = agent.getOutputClass()
        assert output_class == NS.whyis.ImportedResource
    
    def test_importer_crawler_has_query(self):
        """Test that ImporterCrawler has get_query method."""
        agent = autonomic.ImporterCrawler()
        assert hasattr(agent, 'get_query')
        assert callable(agent.get_query)
    
    def test_importer_crawler_with_nanopub(self):
        """Test ImporterCrawler with a nanopublication."""
        self.dry_run = False
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_importer_crawler_rdf, format="turtle")
        
        agent = autonomic.ImporterCrawler()
        
        # Prepare and publish nanopub
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        # Run the agent
        results = self.run_agent(agent)
        
        # Verify it runs without error
        assert isinstance(results, list)
    
    def test_importer_crawler_dry_run(self):
        """Test that ImporterCrawler works in dry run mode."""
        self.dry_run = True
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_importer_crawler_rdf, format="turtle")
        
        agent = autonomic.ImporterCrawler()
        agent.dry_run = True
        
        # Should work in dry run without modifying database
        results = self.run_agent(agent, nanopublication=np)
        
        assert isinstance(results, list)
