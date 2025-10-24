"""
Component tests for DatasetImporter agent.

Tests the dataset importing functionality using the in-memory app infrastructure.
"""

import os
from rdflib import *

from whyis import nanopub
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase


test_dataset_rdf = """
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix void:  <http://rdfs.org/ns/void#> .
@prefix dcat:  <http://www.w3.org/ns/dcat#> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
@prefix :      <http://example.com/dataset/> .

:dataset1 a void:Dataset, dcat:Dataset ;
    rdfs:label "Test Dataset" ;
    void:triples 100 ;
    void:uriSpace "http://example.com/data/" .
"""


class DatasetImporterTestCase(AgentUnitTestCase):
    """Test the DatasetImporter agent functionality."""
    
    def test_dataset_importer_initialization(self):
        """Test that DatasetImporter agent can be initialized."""
        agent = autonomic.DatasetImporter()
        assert agent is not None
        assert hasattr(agent, 'activity_class')
    
    def test_dataset_importer_has_query(self):
        """Test that DatasetImporter has get_query method."""
        agent = autonomic.DatasetImporter()
        assert hasattr(agent, 'get_query')
        assert callable(agent.get_query)
    
    def test_dataset_importer_input_class(self):
        """Test that DatasetImporter returns correct input class."""
        agent = autonomic.DatasetImporter()
        input_class = agent.getInputClass()
        # Should work with Dataset resources
        assert input_class is not None
    
    def test_dataset_importer_output_class(self):
        """Test that DatasetImporter returns correct output class."""
        agent = autonomic.DatasetImporter()
        output_class = agent.getOutputClass()
        # Produces imported dataset
        assert output_class is not None
    
    def test_dataset_importer_with_nanopub(self):
        """Test DatasetImporter with a nanopublication."""
        self.dry_run = False
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_dataset_rdf, format="turtle")
        
        agent = autonomic.DatasetImporter()
        
        # Prepare and publish nanopub
        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        
        # Run the agent
        results = self.run_agent(agent)
        
        # Verify it runs without error
        assert isinstance(results, list)
    
    def test_dataset_importer_dry_run(self):
        """Test that DatasetImporter works in dry run mode."""
        self.dry_run = True
        
        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_dataset_rdf, format="turtle")
        
        agent = autonomic.DatasetImporter()
        agent.dry_run = True
        
        # Should work in dry run without modifying database
        results = self.run_agent(agent, nanopublication=np)
        
        assert isinstance(results, list)
