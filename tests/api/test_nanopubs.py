from rdflib import *

import json

from whyis.test.api_test_case import ApiTestCase


class NanopubTest(ApiTestCase):

    turtle  = '''
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
'''
    
    def test_create(self):
        self.login(*self.create_user("user@example.com","password"))

        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')

        self.assertTrue('Location' in response.headers)

        nanopub = self.app.nanopub_manager.get(URIRef(response.headers['Location']))
        self.assertEquals(len(nanopub), 17)
        self.assertEquals(len(nanopub.assertion), 5)
        self.assertEquals(len(nanopub.pubinfo), 5)
        self.assertEquals(len(nanopub.provenance), 0)

    def test_read(self):
        self.login(*self.create_user("user@example.com","password"))
        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle",follow_redirects=True)
        self.assertEquals(response.status,'201 CREATED')
        self.assertTrue('Location' in response.headers)
        
        nanopub_id = response.headers['Location'].split('/')[-1]
        
        content = self.client.get("/pub/"+nanopub_id,headers={'Accept':'application/json'}, follow_redirects=True)
        g = ConjunctiveGraph()
        self.assertEquals(content.mimetype, "application/json")
        g.parse(data=str(content.data,'utf8'), format="json-ld")
        
        self.assertEquals(len(g), 17)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type), URIRef('http://schema.org/Person'))

    def test_delete_admin(self):
        self.login(*self.create_user("user@example.com","password"))

        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle",follow_redirects=True)
        self.assertEquals(response.status,'201 CREATED')
        self.assertTrue('Location' in response.headers)
        
        nanopub_id = response.headers['Location'].split('/')[-1]
        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status,'204 NO CONTENT')

    def test_delete_nonadmin(self):
        self.login(*self.create_user("user@example.com","password",roles=None))

        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle",follow_redirects=True)
        self.assertEquals(response.status,'201 CREATED')
        self.assertTrue('Location' in response.headers)
        
        nanopub_id = response.headers['Location'].split('/')[-1]

        response = self.client.delete("/pub/"+nanopub_id, follow_redirects=True)
        self.assertEquals(response.status,'204 NO CONTENT')

    def test_linked_data(self):
        self.login(*self.create_user("user@example.com","password"))

        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        
        content = self.client.get("/about",query_string={"uri":"http://example.com/janedoe"},follow_redirects=True)
        g = Graph()
        self.assertEquals(content.mimetype, "text/turtle")
        g.parse(data=str(content.data,'utf8'), format="turtle")
        
        self.assertEquals(len(g), 5)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type), URIRef('http://schema.org/Person'))

        
    def test_attribute_view(self):
        self.login(*self.create_user("user@example.com", "password"))
        response = self.client.post("/pub", data=self.turtle, content_type="text/turtle", follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        
        content = self.client.get("/about",query_string={"uri":"http://example.com/janedoe", 'view':'attributes'},follow_redirects=True)
        
        self.assertEquals(content.mimetype, "application/json")
        json_content = json.loads(str(content.data, 'utf8'))

        self.assertEquals(json_content['label'], "Jane Doe")
        self.assertEquals(len(json_content['type']), 1)
        self.assertEquals(json_content['type'][0]['label'], 'Person')

    def test_ontology_describe_view(self):
        ontology = """
        <http://example.com/> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/2002/07/owl#Ontology> .
        <http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
        <http://schema.org/name> "Jane Doe" ;
        <http://schema.org/telephone> "(425) 123-4567" ;
        <http://schema.org/url> <http://www.janedoe.com> ;
        <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> . """

        self.login(*self.create_user("user@example.com", "password"))
        response = self.client.post("/pub",
                                    data=ontology,
                                    content_type="text/turtle",
                                    follow_redirects=True)
        self.assertStatus(response, 201,
                          "Did not receive '201 CREATED' when publishing ontology nanopub")

        content = self.client.get("/about",
                                  query_string={"uri":"http://example.com/", 'view':'describe'},
                                  follow_redirects=True)
        # Needs blinker installed
        self.assertTemplateUsed("describe_ontology.json")
        self.assertEquals(content.mimetype, "application/json",
                          "Did not receive JSON for 'describe' view")

        data = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(data, list, "'Describe' view returned unexpected structure")
        self.assertTrue(data, "'Describe' view returned empty list")
        self.assertIn("@graph", data[0], "'Describe' view missing @graph key")
        self.assertIn("@id", data[0], "'Describe' view missing @id key")

        graph = data[0]["@graph"]
        self.assertTrue(graph, "'Describe' view returned no subjects")

        for subject in graph:
            if subject["@id"] == "http://example.com/":
                self.assertEquals(len(subject.keys()), 2,
                                  "Subject in 'describe' view has unexpected number of predicates")
            elif subject["@id"] == "http://example.com/janedoe":
                self.assertEquals(len(subject.keys()), 6,
                                  "Subject in 'describe' view has unexpected number of predicates")
