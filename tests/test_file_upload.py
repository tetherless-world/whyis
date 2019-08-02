from testcase import WhyisTestCase

from base64 import b64encode

from rdflib import *

import json
from StringIO import StringIO
from tika import parser as tika_parser


class UploadTest(WhyisTestCase):
    
    def test_plain_text_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        nanopub = '''{ "@id": "http://example.com/testdata","http://vocab.rpi.edu/whyis/hasContent":"data:text/plain;charset=UTF-8,Hello, World!"}'''
        response = self.client.post("/pub", data=nanopub, content_type="application/ld+json",follow_redirects=True)
            
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/testdata"},follow_redirects=True)
        self.assertEquals(content.mimetype, "text/plain")
        self.assertEquals(content.data, "Hello, World!")

    def test_PDF_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        pdf_filename = "tests/test_pdf.pdf"
        pdf_content = u'\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nThis is a test PDF, this is the header. \n\nHello World! This is the body. \nHow are you doing? \n \n  \n\n\n\nThis is a test PDF, this is the header. \n\nThis is page 2. \n\n\n'
        uri = 'http://example.com/testdata_pdf_form_upload'

        pdf_file = open(pdf_filename, "r")
        data = {
            'file': (pdf_file, 'test_pdf.pdf'),
            'upload_type': 'http://purl.org/net/provenance/ns#File'
        }
        response = self.client.post("/about",query_string={"uri":uri}, data=data)
        self.assertEquals(response.status,'302 FOUND')
        content = self.client.get("/about",query_string={"uri":uri},follow_redirects=True)
        self.assertEquals(content.mimetype, "application/pdf")
        self.assertEquals(type(content.data), type("string type"))
        self.assertEquals(tika_parser.from_buffer(content.data)["content"], pdf_content)

        metadata = self.client.get("/about",query_string={"uri":uri, 'view':'describe'},headers={"Accept":"application/ld+json"},follow_redirects=True)
        g = Graph()
        g.parse(data=metadata.data, format="json-ld")
        self.assertTrue(g.resource(URIRef(uri))[RDF.type : URIRef('http://purl.org/net/provenance/ns#File')])

    def test_base64_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        text = "Hello, World!"
        b64text = b64encode(text)
        nanopub = '''{ "@id": "http://example.com/testdatab64","http://vocab.rpi.edu/whyis/hasContent":"data:text/plain;charset=UTF-8;base64,%s"}''' % b64text
        response = self.client.post("/pub", data=nanopub, content_type="application/ld+json",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/testdatab64"},follow_redirects=True)
        self.assertEquals(content.mimetype, "text/plain")
        self.assertEquals(content.data, text)

    def test_form_upload(self):
        self.login(*self.create_user("user@example.com","password"))
        text = "Hello, World!"
        uri = 'http://example.com/testdata_form_upload'
        data = {
            'file': (StringIO(text), 'hello_world.txt'),
            'upload_type': 'http://purl.org/net/provenance/ns#File'
        }
        response = self.client.post("/about",query_string={"uri":uri}, data=data)
        self.assertEquals(response.status,'302 FOUND')
        content = self.client.get("/about",query_string={"uri":uri},follow_redirects=True)
        self.assertEquals(content.mimetype, "text/plain")
        self.assertEquals(content.data, text)

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
        g.parse(data=content.data, format="turtle")
        
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
        b64text = b64encode(text)
        response = self.client.post("/pub", data=turtle, content_type="text/turtle",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        content = self.client.get("/about",query_string={"uri":"http://example.com/janedoe", 'view':'attributes'},follow_redirects=True)
        
        self.assertEquals(content.mimetype, "application/json")
        json_content = json.loads(content.data)

        print json_content

        self.assertEquals(json_content['label'], "Jane Doe")
        self.assertEquals(len(json_content['type']), 1)
        self.assertEquals(json_content['type'][0]['label'], 'Person')
