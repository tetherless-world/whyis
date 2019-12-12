from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json

sio_attributes_turtle = """@prefix ex: <http://example.com/> .
@prefix sio: <http://semanticscience.org/resource/>.
<%s> ex:pred1 "Literal Attribute";
	<http://schema.org/description> "Summary Property";
		sio:hasAttribute [
		a ex:someAttribute;
		sio:hasValue "SomeValue";
	].
""" % PERSON_INSTANCE_URI



class TestAttributesJsonView(ApiTestCase):
    def test_literal_attributes(self):
        self.login_new_user()
        self.post_nanopub(data=PERSON_INSTANCE_TURTLE,
                          content_type="text/turtle")

        content = self.get_view(uri=PERSON_INSTANCE_URI,
                                view="attributes",
                                expected_template="attributes.json",
                                mime_type="application/json")

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertEquals(json_content['label'], "Jane Doe")
        self.assertEquals(len(json_content['type']), 1)
        self.assertEquals(json_content['type'][0]['label'], 'Person')

    def test_sio_attributes(self):
      self.login_new_user()
      self.post_nanopub(data=sio_attributes_turtle, content_type="text/turtle")

      content = self.get_view(uri=PERSON_INSTANCE_URI,
                              view="attributes",
                              expected_template="attributes.json",
                              mime_type="application/json")

      json_content = json.loads(str(content.data, 'utf8'))
      self.assertEquals(json_content['description'][0]['value'], "Summary Property")
      self.assertEquals(json_content['attributes'][0]['values'][0]['value'], "SomeValue")
