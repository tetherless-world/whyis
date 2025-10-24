"""
Component tests for Crawler agent.

Tests the graph crawling functionality using the in-memory app infrastructure.
"""

import os
from rdflib import *

from whyis import nanopub
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase


test_crawler_rdf = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
@prefix whyis: <http://vocab.rpi.edu/whyis/> .
@prefix :      <http://example.com/crawler/> .

:resource1 a whyis:CrawlerStart ;
    foaf:knows :resource2 ;
    rdfs:label "Resource 1" .

:resource2 a foaf:Person ;
    foaf:knows :resource3 ;
    rdfs:label "Resource 2" .

:resource3 a foaf:Person ;
    rdfs:label "Resource 3" .
"""


class CrawlerTestCase(AgentUnitTestCase):
    """Test the Crawler agent functionality."""
    
    def test_crawler_initialization(self):
        """Test that Crawler agent can be initialized."""
        agent = autonomic.Crawler()
        assert agent is not None
        assert hasattr(agent, 'depth')
        assert hasattr(agent, 'predicates')
    
    def test_crawler_with_depth(self):
        """Test Crawler initialization with specific depth."""
        agent = autonomic.Crawler(depth=2)
        assert agent.depth == 2
    
    def test_crawler_with_predicates(self):
        """Test Crawler initialization with specific predicates."""
        predicates = [NS.foaf.knows, NS.rdfs.seeAlso]
        agent = autonomic.Crawler(predicates=predicates)
        assert agent.predicates == predicates
    
    def test_crawler_input_class(self):
        """Test that Crawler returns correct input class."""
        agent = autonomic.Crawler()
        input_class = agent.getInputClass()
        assert input_class == NS.whyis.CrawlerStart
    
    def test_crawler_output_class(self):
        """Test that Crawler returns correct output class."""
        agent = autonomic.Crawler()
        output_class = agent.getOutputClass()
        assert output_class == NS.whyis.Crawled
    
    def test_crawler_custom_node_types(self):
        """Test Crawler with custom node types."""
        custom_input = NS.foaf.Person
        custom_output = NS.foaf.Agent
        agent = autonomic.Crawler(node_type=custom_input, output_node_type=custom_output)
        
        assert agent.getInputClass() == custom_input
        assert agent.getOutputClass() == custom_output
    
    def test_crawler_get_query(self):
        """Test that Crawler generates correct query."""
        agent = autonomic.Crawler()
        query = agent.get_query()
        
        assert isinstance(query, str)
        assert 'select' in query.lower()
        assert '?resource' in query
    
    def test_crawler_with_nanopub(self):
        """Test Crawler with a nanopublication."""
        self.dry_run = False
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_crawler_rdf, format="turtle")
        
        agent = autonomic.Crawler(depth=1)
        
        # Prepare and publish nanopub
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        # Run the agent
        results = self.run_agent(agent)
        
        # Verify it runs without error
        assert isinstance(results, list)
