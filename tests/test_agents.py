from __future__ import print_function
from testcase import WhyisTestCase

from base64 import b64encode

from rdflib import *

import json
from StringIO import StringIO

import nanopub

import autonomic

class OntologyImportAgentTestCase(WhyisTestCase):

    def test_foaf_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data='''{
         "@id": "http://example.com/testonto",
         "@type" : "http://www.w3.org/2002/07/owl#Ontology",
         "http://www.w3.org/2002/07/owl#imports":{"@id":"http://xmlns.com/foaf/0.1/"}
        }''', format="json-ld")
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        self.assertTrue(results[0].resource(URIRef('http://xmlns.com/foaf/0.1/'))[RDF.type:OWL.Ontology])

    def test_dc_terms_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data='''{
         "@id": "http://example.com/testonto",
         "@type" : "http://www.w3.org/2002/07/owl#Ontology",
         "http://www.w3.org/2002/07/owl#imports":{"@id":"http://purl.org/dc/terms/"}
        }''', format="json-ld")
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        print(results[0].serialize(format="trig"))
        self.assertTrue(results[0].resource(URIRef('http://purl.org/dc/terms/created'))[RDF.type:RDF.Property])

    def test_hasco_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data='''{
         "@id": "http://example.com/testonto",
         "@type" : "http://www.w3.org/2002/07/owl#Ontology",
         "http://www.w3.org/2002/07/owl#imports":{"@id":"http://hadatac.org/ont/hasco/"}
        }''', format="json-ld")
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        self.assertTrue(results[0].resource(URIRef('http://hadatac.org/ont/hasco/'))[RDF.type:OWL.Ontology])

    def test_sio_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data='''{
         "@id": "http://example.com/testonto",
         "@type" : "http://www.w3.org/2002/07/owl#Ontology",
         "http://www.w3.org/2002/07/owl#imports":{"@id":"http://semanticscience.org/ontology/sio.owl"}
        }''', format="json-ld")
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        self.assertTrue(results[0].resource(URIRef('http://semanticscience.org/ontology/sio.owl'))[RDF.type:OWL.Ontology])
