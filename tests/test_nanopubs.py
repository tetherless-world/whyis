#from __future__ import print_function
#from future import standard_library
#standard_library.install_aliases()
from testcase import WhyisTestCase

from base64 import b64encode

from rdflib import *

import json
from io import StringIO
from flask_login import login_user

class NanopubTest(WhyisTestCase):
    
    def test_linked_data(self):
        turtle = '''
<http://example.com/janedoe> <http://schema.org/jobTitle> "Professor";
    <http://schema.org/name> "Jane Doe" ;
    <http://schema.org/telephone> "(425) 123-4567" ;
    <http://schema.org/url> <http://www.janedoe.com> ;
    <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
'''        
        self.login(*self.create_user("user@example.com","password"))

        print("POST /pub")
        response = self.client.post("/pub", data=turtle, content_type="text/turtle",follow_redirects=True)
        
        print(response.data, response.status)
        self.assertEquals(response.status,'201 CREATED')
        
        print("GET /about?uri=http://example.com/janedoe&view=attributes")
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
        print("POST /pub")
        response = self.client.post("/pub", data=turtle, content_type="text/turtle",follow_redirects=True)
        
        self.assertEquals(response.status,'201 CREATED')
        
        print("GET /about?uri=http://example.com/janedoe&view=attributes")
        content = self.client.get("/about",query_string={"uri":"http://example.com/janedoe", 'view':'attributes'},follow_redirects=True)
        
        self.assertEquals(content.mimetype, "application/json")
        json_content = json.loads(str(content.data, 'utf8'))

        print(json_content)

        self.assertEquals(json_content['label'], "Jane Doe")
        self.assertEquals(len(json_content['type']), 1)
        self.assertEquals(json_content['type'][0]['label'], 'Person')
