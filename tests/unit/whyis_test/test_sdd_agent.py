import os
from base64 import b64encode

from rdflib import *

import json
from io import StringIO

from whyis import nanopub

import rdflib
from whyis import autonomic
from whyis.namespace import NS
from whyis.test.agent_unit_test_case import AgentUnitTestCase

test_sdd_rdf = """
@prefix rdf:           <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:          <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:           <http://www.w3.org/2001/XMLSchema#> .
@prefix owl:           <http://www.w3.org/2002/07/owl#> .
@prefix prov:          <http://www.w3.org/ns/prov#> .
@prefix dcat:          <http://www.w3.org/ns/dcat#> .
@prefix dcterms:       <http://purl.org/dc/terms/> .
@prefix void:          <http://rdfs.org/ns/void#> .
@prefix setl:          <http://purl.org/twc/vocab/setl/> .
@prefix csvw:          <http://www.w3.org/ns/csvw#> .
@prefix pv:            <http://purl.org/net/provenance/ns#> .
@prefix :              <http://example.com/sdd/> .
@prefix ov: <http://open.vocab.org/terms/> .
@prefix sdd:  <http://purl.org/twc/sdd/> .

<https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/example_sdd.xlsx>
    a dcat:Distribution, sdd:SemanticDataDictionary .

<https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/input/Data/exampleData.csv>
    a dcat:Distribution;
    dcterms:conformsTo <https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/example_sdd.xlsx>;
    ov:hasContentType "text/csv";
    csvw:delimiter "," .

:dataset a void:Dataset, dcat:Dataset;
  void:uriSpace "http://example.com/sdd/graph/";
  dcat:distribution
    <https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/example_sdd.xlsx>,
    <https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/input/Data/exampleData.csv> .
"""

class SDDAgentTestCase(AgentUnitTestCase):

    def test_basic_sdd(self):
        self.dry_run = False

        np = nanopub.Nanopublication()
        np.assertion.parse(data=test_sdd_rdf, format="turtle")
        #print(np.serialize(format="trig"))
        agent = autonomic.SDDAgent()

        nanopubs = self.app.nanopub_manager.prepare(np)
        self.app.nanopub_manager.publish(*nanopubs)
        results = self.run_agent(agent)
        nanopubs = list(self.app.db.query(
            ''' select distinct ?np where {?np a np:Nanopublication}''',
            initNs=NS.prefixes))
        self.assertEqual(len(nanopubs),4)

        invocations = list(self.app.db.query('''select distinct ?sdd_file ?dataset ?data_file where {
            ?setl_script prov:wasDerivedFrom ?sdd_file;
                a setl:SemanticETLScript.
            ?dataset prov:wasGeneratedBy ?setl_script;
                prov:wasGeneratedBy ?template.
            ?template a setl:Transform;
                prov:used/prov:wasGeneratedBy ?extract.
            ?extract a setl:Extract;
                prov:used ?data_file.
        }''', initBindings=dict(
            sdd_file=rdflib.URIRef('https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/example_sdd.xlsx'),
            data_file=rdflib.URIRef('https://raw.githubusercontent.com/tetherless-world/SemanticDataDictionary/master/ExampleProject/input/Data/exampleData.csv')
            ), initNs=NS.prefixes ))
        self.assertEqual(len(invocations),1)
