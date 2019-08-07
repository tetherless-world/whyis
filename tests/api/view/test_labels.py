from ..api_test_data import HOME_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json


class TestLabels(ApiTestCase):
    def test(self):
        self.login_new_user()

        content = self.get_view(uri=HOME_INSTANCE_URI,
                                view="labels",
                                expected_template="labels.json",
                                mime_type="application/json",
                                query_string={"uris": HOME_INSTANCE_URI}
                                )

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(json_content, dict)
        self.assertEquals(len(json_content), 1)
        self.assertEqual(json_content[HOME_INSTANCE_URI], "Home")
