"""
Component tests for CacheUpdater agent.

Tests the cache updating functionality using the in-memory app infrastructure.
"""

import os
from rdflib import *

from whyis import nanopub
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase


test_cache_rdf = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
@prefix :      <http://example.com/test/> .

:TestResource a owl:Class .

:person1 a :TestResource ;
    foaf:name "Alice" ;
    foaf:age 30 .

:person2 a :TestResource ;
    foaf:name "Bob" ;
    foaf:age 25 .
"""


class CacheUpdaterTestCase(AgentUnitTestCase):
    """Test the CacheUpdater agent functionality."""
    
    def test_cache_updater_initialization(self):
        """Test that CacheUpdater agent can be initialized."""
        agent = autonomic.CacheUpdater()
        assert agent is not None
        assert hasattr(agent, 'activity_class')
    
    def test_cache_updater_has_query(self):
        """Test that CacheUpdater has get_query method."""
        agent = autonomic.CacheUpdater()
        assert hasattr(agent, 'get_query')
        assert callable(agent.get_query)
    
    def test_cache_updater_input_class(self):
        """Test that CacheUpdater returns correct input class."""
        agent = autonomic.CacheUpdater()
        input_class = agent.getInputClass()
        assert input_class == NS.RDFS.Resource
    
    def test_cache_updater_output_class(self):
        """Test that CacheUpdater returns correct output class."""
        agent = autonomic.CacheUpdater()
        output_class = agent.getOutputClass()
        assert output_class == NS.whyis.CachedResource
    
    def test_cache_updater_with_nanopub(self):
        """Test CacheUpdater with a nanopublication."""
        self.dry_run = False
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_cache_rdf, format="turtle")
        
        agent = autonomic.CacheUpdater()
        
        # Prepare and publish nanopub
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        # Run the agent (may not produce results if cache is not configured)
        results = self.run_agent(agent)
        
        # Just verify it runs without error
        assert isinstance(results, list)
