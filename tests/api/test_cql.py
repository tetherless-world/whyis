import json
from rdflib import ConjunctiveGraph, Graph, URIRef
from rdflib.namespace import RDF
from whyis.test.api_test_case import ApiTestCase

from .api_test_data import PERSON_INSTANCE_TURTLE

class TestCQLAPI(ApiTestCase):
    turtle = PERSON_INSTANCE_TURTLE

    def test_cql_form_redirect(self):
        self.login_new_user()
        response = self.post_nanopub(data=self.turtle,
                                       content_type="text/turtle",
                                       expected_headers=["Location"])

        content = self.client.get("/cql", follow_redirects=False)
        
        self.assertEquals(content.status,'302 FOUND')
        self.assertEquals(content.headers['Location'], 'http://localhost/cql.html')

    def test_cql_translate_only(self):
        """Test that translate-only parameter returns SPARQL query as plain text"""
        self.login_new_user()
        
        # Test with translate-only parameter
        cql_query = "MATCH (p:Person) RETURN p"
        response = self.client.post("/cql", 
                                   data={"query": cql_query, "translate-only": "true"},
                                   follow_redirects=False)
        
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content_type, 'text/plain; charset=utf-8')
        
        # Check that response contains SPARQL-like content
        response_text = response.get_data(as_text=True)
        self.assertIn("SELECT", response_text)
        self.assertIn("WHERE", response_text)

    def test_cql_query_execution(self):
        """Test that CQL query gets translated and executed"""
        self.login_new_user()
        
        # Add some test data first
        response = self.post_nanopub(data=self.turtle,
                                       content_type="text/turtle",
                                       expected_headers=["Location"])
        
        # Test CQL query execution (without translate-only)
        cql_query = "MATCH (p:Person) RETURN p"
        response = self.client.post("/cql", 
                                   data={"query": cql_query},
                                   follow_redirects=False)
        
        # Should get some kind of result (not plain text)
        self.assertEquals(response.status_code, 200)
        self.assertNotEquals(response.content_type, 'text/plain; charset=utf-8')