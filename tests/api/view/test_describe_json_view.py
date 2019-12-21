from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json


class TestDescribeJsonView(ApiTestCase):
    def test(self):
        self.login_new_user()
        self.post_nanopub(data=PERSON_INSTANCE_TURTLE,
                          content_type="text/turtle")

        content = self.get_view(uri=PERSON_INSTANCE_URI,
                                view="describe",
                                expected_template="describe.json",
                                mime_type="application/json")

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(json_content, list)
        self.assertEqual(1, len(json_content))
        description = json_content[0]
        self.assertIsInstance(description, dict)
        self.assertEqual(description["@id"], PERSON_INSTANCE_URI)
        self.assertEqual(description["http://schema.org/jobTitle"], [{"@value": "Professor"}])

# TODO Tests where the URI is a resource, ontology, class, or nanopub, since each of those has their own json template
