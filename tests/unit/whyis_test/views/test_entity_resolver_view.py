
import json
from rdflib import ConjunctiveGraph, Graph, URIRef, BNode
from rdflib.namespace import RDF
from whyis.test.api_test_case import ApiTestCase

from whyis.nanopub import Nanopublication

from .api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_TRIG, PERSON_INSTANCE_BNODE_TURTLE


class TestEntityResolverView(ApiTestCase):
    def test_skos_notation_lookup(self):
        self.login_new_user()
        response = self.post_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])
        nanopub_id = response.headers['Location'].split('/')[-1]
        content = self.client.get("/pub/"+nanopub_id,
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        g = ConjunctiveGraph()
        self.assertEquals(content.mimetype, "application/json")
        g.parse(data=str(content.data, 'utf8'), format="json-ld")
        
        self.assertEquals(len(g), 15)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type),
                          URIRef('http://schema.org/Person'))
