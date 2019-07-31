
import json
from rdflib import ConjunctiveGraph, Graph, URIRef
from rdflib.namespace import RDF
from whyis.test.api_test_case import ApiTestCase


class NanopubTest(ApiTestCase):

    turtle = '''
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
'''

    def test_create(self):
        self.login_new_user()
        response = self.publish_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub = self.app.nanopub_manager.get(URIRef(response.headers['Location']))
        self.assertEquals(len(nanopub), 17)
        self.assertEquals(len(nanopub.assertion), 5)
        self.assertEquals(len(nanopub.pubinfo), 5)
        self.assertEquals(len(nanopub.provenance), 0)

    def test_read(self):
        self.login_new_user()
        response = self.publish_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location'].split('/')[-1]
        content = self.client.get("/pub/"+nanopub_id,
                                  headers={'Accept':'application/json'},
                                  follow_redirects=True)
        g = ConjunctiveGraph()
        self.assertEquals(content.mimetype, "application/json")
        g.parse(data=str(content.data, 'utf8'), format="json-ld")

        self.assertEquals(len(g), 17)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type),
                          URIRef('http://schema.org/Person'))

    def test_delete_admin(self):
        self.login_new_user()
        response = self.publish_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location'].split('/')[-1]
        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status, '204 NO CONTENT')

    def test_delete_nonadmin(self):
        self.login_new_user(role=None)
        response = self.publish_nanopub(data=self.turtle,
                                        content_type="text/turtle",
                                        expected_headers=["Location"])

        nanopub_id = response.headers['Location'].split('/')[-1]
        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status, '204 NO CONTENT')

    def test_delete_invalid(self):
        self.login(*self.create_user("user1@example.com","password",roles=None))

        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle",follow_redirects=True)
        self.assertEquals(response.status,'201 CREATED')
        self.assertTrue('Location' in response.headers)
        
        nanopub_id = response.headers['Location'].split('/')[-1]

        self.login(*self.create_user("user2@example.com","password",roles=None))
        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status,'401 UNAUTHORIZED')

    def test_linked_data(self):
        self.login_new_user()
        self.publish_nanopub(data=self.turtle,
                             content_type="text/turtle")

        # Because of (lack of) content negotiation
        content = self.get_view(uri="http://example.com/janedoe",
                                mime_type="text/turtle")

        g = Graph()
        g.parse(data=str(content.data, 'utf8'), format="turtle")

        self.assertEquals(len(g), 5)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type),
                          URIRef('http://schema.org/Person'))

    def test_mime_behavior(self):
        self.login_new_user()
        self.publish_nanopub(data=self.turtle,
                             content_type="text/turtle")

        self.get_view(uri="http://example.com/janedoe",
                      mime_type="text/turtle",
                      expected_template="describe.json")

        self.get_view(uri="http://example.com/janedoe",
                      headers={'Accept': 'text/html'},
                      mime_type="text/html",
                      expected_template="resource_view.html")

    def test_attribute_view(self):
        self.login_new_user()
        self.publish_nanopub(data=self.turtle,
                             content_type="text/turtle")

        content = self.get_view(uri="http://example.com/janedoe",
                                view="attributes",
                                mime_type="application/json")

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertEquals(json_content['label'], "Jane Doe")
        self.assertEquals(len(json_content['type']), 1)
        self.assertEquals(json_content['type'][0]['label'], 'Person')

    def test_ontology_describe_view(self):
        self.login_new_user()
        ontology = """
        <http://example.com/> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
        <http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
        <http://schema.org/name> "Jane Doe" ;
        <http://schema.org/telephone> "(425) 123-4567" ;
        <http://schema.org/url> <http://www.janedoe.com> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> . """

        self.publish_nanopub(data=ontology,
                             content_type="text/turtle")

        content = self.get_view(uri="http://example.com/",
                                view="describe",
                                mime_type="application/json",
                                expected_template="describe_ontology.json")

        data = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(data, list, "'describe' view returned unexpected structure")
        self.assertTrue(data, "'describe' view returned empty list")
        self.assertIn("@graph", data[0], "'describe' view missing @graph key")
        self.assertIn("@id", data[0], "'describe' view missing @id key for graph")

        graph = data[0]["@graph"]
        self.assertEqual(len(graph), 2, "'describe' view returned the wrong number of subjects")

        for subject in graph:
            if subject["@id"] == "http://example.com/":
                self.assertEqual(len(subject.keys()), 2,
                                 "Subject in 'describe' view has unexpected number of predicates")
                self.assertIn("http://www.w3.org/2002/07/owl#Ontology", subject["@type"],
                              "Expected an ontology type object in the 'describe' view")
            elif subject["@id"] == "http://example.com/janedoe":
                self.assertEqual(len(subject.keys()), 6,
                                 "Subject in 'describe' view has unexpected number of predicates")
