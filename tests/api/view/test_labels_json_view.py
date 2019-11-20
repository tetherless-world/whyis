from whyis.test.api_test_case import ApiTestCase
import json


class TestLabelsJsonView(ApiTestCase):
    def test(self):
        try:
            import config
        except:
            from whyis import config_defaults as config
        
        HOME_INSTANCE_URI = config.LOD_PREFIX + "/Home"

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
