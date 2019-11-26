
import json
from rdflib import ConjunctiveGraph, Graph, URIRef, BNode, Namespace, Literal
from rdflib.namespace import RDF
from whyis.test.api_test_case import ApiTestCase

TEST_DATA_TURTLE = '''
@prefix skos: <http://www.w3.org/2004/02/skos/core#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix : <http://example.com/>.

:centimeter a :UnitOfMeasure;
  skos:notation "cm";
  rdfs:label "centimeter".
'''
bds = Namespace("http://www.bigdata.com/rdf/search#")


class TestEntityResolverView(ApiTestCase):
    def test_skos_notation_lookup(self):
        self.login_new_user()
        response = self.post_nanopub(data=TEST_DATA_TURTLE,
                                     content_type="text/turtle",
                                     expected_headers=["Location"])
        self.app.db.add((Literal("cm"), bds.search, Literal("cm")))
        self.app.db.add((Literal("cm"), bds.matchAllTerms, Literal("false")))
        self.app.db.add((Literal("cm"), bds.relevance, Literal(1.0)))
        content = self.client.get("/?view=resolve&term=cm",
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        results = json.loads(content.data.decode('utf8'))
        self.assertEquals(len(results),1)
        self.assertEquals(results[0]['node'], "http://example.com/centimeter")

    def test_rdfs_label_lookup(self):
        self.login_new_user()
        response = self.post_nanopub(data=TEST_DATA_TURTLE,
                                     content_type="text/turtle",
                                     expected_headers=["Location"])
        self.app.db.add((Literal("centimeter"), bds.search, Literal("centimeter")))
        self.app.db.add((Literal("centimeter"), bds.matchAllTerms, Literal("false")))
        self.app.db.add((Literal("centimeter"), bds.relevance, Literal(1.0)))
        content = self.client.get("/?view=resolve&term=centimeter",
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        results = json.loads(content.data.decode('utf8'))
        self.assertEquals(len(results),1)
        self.assertEquals(results[0]['node'], "http://example.com/centimeter")

    def test_rdfs_label_partial_lookup(self):
        self.login_new_user()
        response = self.post_nanopub(data=TEST_DATA_TURTLE,
                                     content_type="text/turtle",
                                     expected_headers=["Location"])
        self.app.db.add((Literal("centimeter"), bds.search, Literal("centi")))
        self.app.db.add((Literal("centimeter"), bds.matchAllTerms, Literal("false")))
        self.app.db.add((Literal("centimeter"), bds.relevance, Literal(1.0)))
        content = self.client.get("/?view=resolve&term=centi",
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        results = json.loads(content.data.decode('utf8'))
        self.assertEquals(len(results),1)
        self.assertEquals(results[0]['node'], "http://example.com/centimeter")
