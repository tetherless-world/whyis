#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()

from base64 import b64encode

from rdflib import *

import json
from io import StringIO

import nanopub

import autonomic
from .unit_test_case import UnitTestCase


class OntologyImportAgentTestCase(UnitTestCase):

    def test_foaf_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data='''{
         "@id": "http://example.com/testonto",
         "@type" : "http://www.w3.org/2002/07/owl#Ontology",
         "http://www.w3.org/2002/07/owl#imports":{"@id":"http://xmlns.com/foaf/0.1/"}
        }''', format="json-ld")
        #print(np.serialize(format="trig"))
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        self.assertTrue(results[0].resource(URIRef('http://xmlns.com/foaf/0.1/'))[RDF.type:OWL.Ontology])

    def test_dc_terms_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data=str('''<http://example.com/testonto> a <http://www.w3.org/2002/07/owl#Ontology>;
         <http://www.w3.org/2002/07/owl#imports> <http://purl.org/dc/terms/>.'''), format="turtle")
        #print(np.serialize(format="trig"))
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        #print(results[0].serialize(format="trig"))
        self.assertTrue(results[0].resource(URIRef('http://purl.org/dc/terms/created'))[RDF.type:RDF.Property])

    def test_prov_import(self):
        np = nanopub.Nanopublication()
        np.assertion.parse(data='''{
         "@id": "http://example.com/testonto",
         "@type" : "http://www.w3.org/2002/07/owl#Ontology",
         "http://www.w3.org/2002/07/owl#imports":{"@id":"http://www.w3.org/ns/prov#"}
        }''', format="json-ld")
        #print(np.serialize(format="trig"))
        agent = autonomic.OntologyImporter()

        results = self.run_agent(agent, nanopublication=np)
        self.assertEquals(len(results), 1)
        self.assertTrue(len(results[0]) > 0)
        self.assertTrue(results[0].resource(URIRef('http://www.w3.org/ns/prov#'))[RDF.type:OWL.Ontology])

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
