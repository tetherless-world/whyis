#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()
from testcase import WhyisTestCase

from base64 import b64encode

from rdflib import *

import json
from io import StringIO
from flask_login import login_user

class UploadTest(WhyisTestCase):
    
    def test_plain_text_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        
        nanopub = '''{ "@id": "http://example.com/testdata","http://vocab.rpi.edu/whyis/hasContent":"data:text/plain;charset=UTF-8,Hello, World!"}'''
        response = self.client.post("/pub", data=nanopub, content_type="application/ld+json",follow_redirects=True)
        print (response.data)
            
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/testdata"},follow_redirects=True)
        self.assertEquals(content.mimetype, "text/plain")
        self.assertEquals(str(content.data,'utf8'), "Hello, World!")    

    def test_base64_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        text = "Hello, World!"
        b64text = str(b64encode(bytes(text,'utf8')),'utf8')
        nanopub = '''{ "@id": "http://example.com/testdatab64","http://vocab.rpi.edu/whyis/hasContent":"data:text/plain;charset=UTF-8;base64,%s"}''' % b64text
        response = self.client.post("/pub", data=bytes(nanopub,'utf8'), content_type="application/ld+json",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/testdatab64"},follow_redirects=True)
        self.assertEquals(content.mimetype, "text/plain")
        self.assertEquals(str(content.data, 'utf8'), text)

    def test_form_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        text = "Hello, World!"
        uri = 'http://example.com/testdata_form_upload'
        data = {
            'file': (bytes(text,'utf8'), 'hello_world.txt'),
            'upload_type': 'http://purl.org/net/provenance/ns#File'
        }
        response = self.client.post("/about",query_string={"uri":uri}, data=data)
        self.assertEquals(response.status,'302 FOUND')
        content = self.client.get("/about",query_string={"uri":uri},follow_redirects=True)
        self.assertEquals(content.mimetype, "text/plain")
        self.assertEquals(str(content.data, 'utf8'), text)

        metadata = self.client.get("/about",query_string={"uri":uri, 'view':'describe'},headers={"Accept":"application/ld+json"},follow_redirects=True)
        g = Graph()
        g.parse(data=metadata.data, format="json-ld")
        self.assertTrue(g.resource(URIRef(uri))[RDF.type : URIRef('http://purl.org/net/provenance/ns#File')])

        
    def test_linked_data(self):
        turtle = '''
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
'''        
        self.login(*self.create_user("user@example.com","password"))
        response = self.client.post("/pub", data=turtle, content_type="text/turtle",follow_redirects=True)
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/janedoe"},follow_redirects=True)
        g = Graph()
        self.assertEquals(content.mimetype, "text/turtle")
        g.parse(data=str(content.data,'utf8'), format="turtle")
        
        self.assertEquals(len(g), 5)
        self.assertEquals(g.value(URIRef('http://example.com/janedoe'), RDF.type), URIRef('http://schema.org/Person'))

    def test_attribute_view(self):
        turtle = '''
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
'''        
        self.login(*self.create_user("user@example.com","password"))
        text = "Hello, World!"
        b64text = b64encode(bytes(text,'utf8'))
        response = self.client.post("/pub", data=turtle, content_type="text/turtle",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/janedoe", 'view':'attributes'},follow_redirects=True)
        
        self.assertEquals(content.mimetype, "application/json")
        json_content = json.loads(str(content.data, 'utf8'))

        print(json_content)

        self.assertEquals(json_content['label'], "Jane Doe")
        self.assertEquals(len(json_content['type']), 1)
        self.assertEquals(json_content['type'][0]['label'], 'Person')
