from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json


class TestNanopublicationsJsonView(ApiTestCase):
    def test(self):
        try:
            import config
        except:
            from whyis import config_defaults as config
        
        self.login_new_user()
        response = self.post_nanopub(data=PERSON_INSTANCE_TURTLE,
                                     content_type="text/turtle")

        print(response.headers['Location'])
        
        content = self.get_view(uri=PERSON_INSTANCE_URI,
                                view="nanopublications",
                                expected_template="nanopublications.json",
                                mime_type="application/json")

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(json_content, list)
        self.assertEqual(1, len(json_content))
        nanopublication = json_content[0]
        self.assertIsInstance(nanopublication, dict)
        self.assertEqual(nanopublication["contributor"], config.LOD_PREFIX + '/user/identifier')
