from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI
from whyis.test.api_test_case import ApiTestCase
import json
from urllib.parse import quote_plus

uriNone = 'http://example.com/summaryTest2'
dataNone = '<http://example.com/summaryTest2> <http://example.com/irrelevantProperty> "irrelevant property".'

uriCustom = 'http://example.com/summaryTest1'
dataCustom = '<http://example.com/summaryTest3> <http://example.com/summaryTestProperty> "custom property".'


class TestSummaryJsonView(ApiTestCase):
    def test_summary(self):
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

    def test_summary_none(self):
      self.login_new_user()
      self.post_nanopub(data = dataNone, content_type="text/turtle")

      response = self.client.get("/?view=summary&uri="+quote_plus(uriNone))
      self.assertEquals(len(response.json), 0)

    def test_summary_custom(self):

      self.login_new_user()
      self.post_nanopub(data = dataCustom, content_type="text/turtle")

      response = self.client.get("/?view=summary&uri="+quote_plus(uriCustom))
      self.assertEquals(response.json, [ ['http://example.com/summaryTestProperty', 'custom property'] ])
