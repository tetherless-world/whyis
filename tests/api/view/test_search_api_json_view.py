from ..api_test_data import PERSON_INSTANCE_TURTLE, PERSON_INSTANCE_URI, LOD_PREFIX
from whyis.test.api_test_case import ApiTestCase
import json


class TestSearchApiJsonView(ApiTestCase):
    def test(self):
        self.login_new_user()
        self.post_nanopub(data=PERSON_INSTANCE_TURTLE,
                          content_type="text/turtle")

        content = self.client.get("/searchApi",
                                  query_string={"query": "Jane"},
                                  follow_redirects=True)

        self.assertEqual("\n", str(content.data, "utf8"))
