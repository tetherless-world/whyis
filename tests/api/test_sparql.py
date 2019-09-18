
import json
from rdflib import ConjunctiveGraph, Graph, URIRef
from rdflib.namespace import RDF
from whyis.test.api_test_case import ApiTestCase

from .api_test_data import PERSON_INSTANCE_TURTLE

class TestSPARQLAPI(ApiTestCase):
    turtle = PERSON_INSTANCE_TURTLE


    def test_sparql_form_redirect(self):
        self.login_new_user()
        response = self.post_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        content = self.client.get("/sparql", follow_redirects=False)
        
        self.assertEquals(content.status,'302 FOUND')
        self.assertEquals(content.headers['Location'], 'http://localhost/sparql.html')
