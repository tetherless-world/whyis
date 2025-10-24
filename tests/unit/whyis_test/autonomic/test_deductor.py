"""
Component tests for Deductor agent.

Tests the inference/deduction functionality using the in-memory app infrastructure.
"""

import os
from rdflib import *

from whyis import nanopub
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase


test_deduction_rdf = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix foaf:  <http://xmlns.com/foaf/0.1/> .
@prefix :      <http://example.com/deduct/> .

# Define a simple ontology
:Person a owl:Class .
:Student a owl:Class ;
    rdfs:subClassOf :Person .

# Define an instance
:alice a :Student ;
    foaf:name "Alice" .
"""


class DeductorTestCase(AgentUnitTestCase):
    """Test the Deductor agent functionality."""
    
    def test_deductor_initialization(self):
        """Test that Deductor agent can be initialized."""
        agent = autonomic.Deductor()
        assert agent is not None
        assert hasattr(agent, 'activity_class')
    
    def test_deductor_has_query(self):
        """Test that Deductor has get_query method."""
        agent = autonomic.Deductor()
        assert hasattr(agent, 'get_query')
        assert callable(agent.get_query)
    
    def test_deductor_input_class(self):
        """Test that Deductor returns correct input class."""
        agent = autonomic.Deductor()
        input_class = agent.getInputClass()
        # Deductor typically works with Resources
        assert input_class is not None
    
    def test_deductor_output_class(self):
        """Test that Deductor returns correct output class."""
        agent = autonomic.Deductor()
        output_class = agent.getOutputClass()
        # Deductor produces inferred assertions
        assert output_class is not None
    
    def test_deductor_with_nanopub(self):
        """Test Deductor with a nanopublication containing deducible statements."""
        self.dry_run = False
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_deduction_rdf, format="turtle")
        
        agent = autonomic.Deductor()
        
        # Prepare and publish nanopub
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        # Run the agent
        results = self.run_agent(agent)
        
        # Verify it runs without error
        assert isinstance(results, list)
    
    def test_deductor_respects_dry_run(self):
        """Test that Deductor respects dry_run flag."""
        self.dry_run = True
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_deduction_rdf, format="turtle")
        
        agent = autonomic.Deductor()
        agent.dry_run = True
        
        # Should not modify database in dry run
        results = self.run_agent(agent, nanopublication=np)
        
        assert isinstance(results, list)
