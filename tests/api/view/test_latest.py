from ..api_test_data import HOME_INSTANCE_URI, PERSON_INSTANCE_TURTLE
from whyis.test.api_test_case import ApiTestCase
import json


class TestLatest(ApiTestCase):
    def test(self):
        self.login_new_user()

        self.post_nanopub(data=PERSON_INSTANCE_TURTLE,
                          content_type="text/turtle")

        content = self.get_view(uri=HOME_INSTANCE_URI,
                                view="latest",
                                expected_template="latest.json",
                                mime_type="application/json",
                                )

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(json_content, list)
        self.assertEquals(len(json_content), 0)
