
import json
from rdflib import ConjunctiveGraph, Graph, URIRef, BNode
from rdflib.namespace import RDF
from whyis.test.api_test_case import ApiTestCase

from whyis.nanopub import Nanopublication

from .api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_TRIG, PERSON_INSTANCE_BNODE_TURTLE


class TestNanopubCrud(ApiTestCase):
    turtle = PERSON_INSTANCE_TURTLE

    def test_create(self):
        self.login_new_user()
        response = self.post_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub = self.app.nanopub_manager.get(URIRef(response.headers['Location']))
        self.assertEquals(len(nanopub.assertion), 6)
        self.assertEquals(len(nanopub.pubinfo), 2)
        self.assertEquals(len(nanopub.provenance), 0)
        self.assertEquals(len(nanopub), 15)

    def test_bnode_rewrite(self):
        self.login_new_user()
        self.app.config['BNODE_REWRITE'] = True
        response = self.post_nanopub(data=PERSON_INSTANCE_BNODE_TURTLE,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        rewritten_bnode_subjects = [s for s,p,o,context in self.app.db.quads()
                                    if isinstance(s, URIRef) and s.startswith('bnode:')]
        bnode_subjects = [s for s,p,o,context in self.app.db.quads() if isinstance(s, BNode)]
        self.assertEquals(len(rewritten_bnode_subjects),1)
        self.assertEquals(len(bnode_subjects), 0)

        # Nanopublication bnodes should, when retrieved, get turned back into bnodes
        nanopub = self.app.nanopub_manager.get(URIRef(response.headers['Location']))
        rewritten_bnode_subjects = [s for s,p,o,context in nanopub.quads()
                                    if isinstance(s, URIRef) and s.startswith('bnode:')]
        bnode_subjects = [s for s,p,o,context in nanopub.quads() if isinstance(s, BNode)]
        self.assertEquals(len(rewritten_bnode_subjects),0)
        self.assertEquals(len(bnode_subjects), 1)

    def test_no_bnode_rewrite(self):
        self.app.config['BNODE_REWRITE'] = False
        self.login_new_user()
        response = self.post_nanopub(data=PERSON_INSTANCE_BNODE_TURTLE,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub = self.app.nanopub_manager.get(URIRef(response.headers['Location']))
        rewritten_bnode_subjects = [s for s,p,o,context in nanopub.quads()
                                    if isinstance(s, URIRef) and s.startswith('bnode:')]
        bnode_subjects = [s for s,p,o,context in nanopub.quads() if isinstance(s, BNode)]
        self.assertEquals(len(rewritten_bnode_subjects),0)
        self.assertEquals(len(bnode_subjects), 1)
        
    def test_read(self):
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

    def test_read_custom_graph(self):
        self.login_new_user()
        nanopub = Nanopublication(identifier=URIRef("http://example.com/janedoe/info"))
        nanopub.assertion.parse(data=self.turtle, format="turtle")
        trig = ConjunctiveGraph(store=nanopub.store).serialize(format='trig')
        response = self.post_nanopub(data=trig,
                                        content_type="application/trig",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location']
        self.assertEquals(nanopub_id, "http://example.com/janedoe/info")
        content = self.client.get("/about?uri="+nanopub_id,
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        g = ConjunctiveGraph()
        self.assertEquals(content.mimetype, "application/json")
        g.parse(data=str(content.data, 'utf8'), format="json-ld")

        self.assertEquals(len(g), 15)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type),
                          URIRef('http://schema.org/Person'))

    def test_read_bnode_graph(self):
        self.login_new_user()
        response = self.post_nanopub(data=PERSON_INSTANCE_TRIG,
                                        content_type="application/trig",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location']
        content = self.client.get("/about?uri="+nanopub_id,
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        g = ConjunctiveGraph()
        self.assertEquals(content.mimetype, "application/json")
        g.parse(data=str(content.data, 'utf8'), format="json-ld")

        self.assertEquals(len(g), 15)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type),
                          URIRef('http://schema.org/Person'))
        
    def test_delete_admin(self):
        self.login_new_user()
        response = self.post_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location'].split('/')[-1]
        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status, '204 NO CONTENT')

    def test_delete_nonadmin(self):
        self.login_new_user(role=None)
        response = self.post_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location'].split('/')[-1]
        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status, '204 NO CONTENT')

    def test_delete_invalid(self):
        self.login_new_user(email="user1@example.com", username="identifier1", role=None)

        response = self.post_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location'].split('/')[-1]

        self.client.post("/logout", follow_redirects=True)
        self.login_new_user(email="user2@example.com", username="identifier2", role=None)

        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status,'401 UNAUTHORIZED')

    def test_linked_data(self):
        self.login_new_user()
        self.post_nanopub(data=self.turtle,
                             content_type="text/turtle")

        # Because of (lack of) content negotiation
        content = self.get_view(uri="http://example.com/janedoe",
                                mime_type="text/turtle")

        g = Graph()
        g.parse(data=str(content.data, 'utf8'), format="turtle")

        self.assertEquals(len(g), 6)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type),
                          URIRef('http://schema.org/Person'))

    def test_mime_behavior(self):
        self.login_new_user()
        self.post_nanopub(data=self.turtle,
                             content_type="text/turtle")

        self.get_view(uri="http://example.com/janedoe",
                      mime_type="text/turtle",
                      expected_template="describe.json")

        self.get_view(uri="http://example.com/janedoe",
                      headers={'Accept': 'text/html'},
                      mime_type="text/html",
                      expected_template="resource_view.html")


