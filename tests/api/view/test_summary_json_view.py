from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json


class TestSummaryJsonView(ApiTestCase):
    def test(self):
        self.login_new_user()
        self.post_nanopub(data=PERSON_INSTANCE_TURTLE,
                          content_type="text/turtle")

        content = self.get_view(uri=PERSON_INSTANCE_URI,
                                view="summary",
                                expected_template="summary_view.json",
                                mime_type="application/json")

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(json_content, list)
        self.assertEqual(1, len(json_content))
        summary_properties = json_content[0]
        self.assertIsInstance(summary_properties, list)
        self.assertEqual(summary_properties[0], 'http://purl.org/dc/terms/description')
        self.assertEqual(summary_properties[1], 'Jane Doe is a person')
