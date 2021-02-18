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
        if isinstance(json_content, list):
            self.assertEqual(1, len(json_content))
            description = json_content[0]
        else:
            description = json_content
        print(description)
        self.assertIsInstance(description, dict)
        self.assertEqual(description["@id"], PERSON_INSTANCE_URI)
        if '@context' in description and 'schema' in description['@context']:
            self.assertEqual(description["schema:jobTitle"], "Professor")
        else:
            self.assertEqual(description["http://schema.org/jobTitle"], [{"@value": "Professor"}])
