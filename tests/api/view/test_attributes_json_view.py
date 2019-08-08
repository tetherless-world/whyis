from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json


class TestAttributesJsonView(ApiTestCase):
    def test(self):
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
