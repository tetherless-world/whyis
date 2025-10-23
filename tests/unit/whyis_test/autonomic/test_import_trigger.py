"""
Component tests for ImportTrigger agent.

Tests the import triggering functionality using the in-memory app infrastructure.
"""

import os
from rdflib import *

from whyis import nanopub
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase


test_import_trigger_rdf = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix whyis: <http://vocab.rpi.edu/whyis/> .
@prefix :      <http://example.com/import/> .

:entity1 a whyis:Entity ;
    rdfs:label "Test Entity" ;
    rdfs:comment "This should trigger import" .
"""


class ImportTriggerTestCase(AgentUnitTestCase):
    """Test the ImportTrigger agent functionality."""
    
    def test_import_trigger_initialization(self):
        """Test that ImportTrigger agent can be initialized."""
        agent = autonomic.ImportTrigger()
        assert agent is not None
        assert hasattr(agent, 'activity_class')
    
    def test_import_trigger_input_class(self):
        """Test that ImportTrigger returns correct input class."""
        agent = autonomic.ImportTrigger()
        input_class = agent.getInputClass()
        assert input_class == NS.whyis.Entity
    
    def test_import_trigger_output_class(self):
        """Test that ImportTrigger returns correct output class."""
        agent = autonomic.ImportTrigger()
        output_class = agent.getOutputClass()
        assert output_class == NS.whyis.ImportedEntity
    
    def test_import_trigger_has_query(self):
        """Test that ImportTrigger has get_query method."""
        agent = autonomic.ImportTrigger()
        assert hasattr(agent, 'get_query')
        assert callable(agent.get_query)
    
    def test_import_trigger_with_nanopub(self):
        """Test ImportTrigger with a nanopublication."""
        self.dry_run = False
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_import_trigger_rdf, format="turtle")
        
        agent = autonomic.ImportTrigger()
        
        # Prepare and publish nanopub
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        # Run the agent
        results = self.run_agent(agent)
        
        # Verify it runs without error
        assert isinstance(results, list)
    
    def test_import_trigger_dry_run(self):
        """Test that ImportTrigger works in dry run mode."""
        self.dry_run = True
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_import_trigger_rdf, format="turtle")
        
        agent = autonomic.ImportTrigger()
        agent.dry_run = True
        
        # Should work in dry run without modifying database
        results = self.run_agent(agent, nanopublication=np)
        
        assert isinstance(results, list)
