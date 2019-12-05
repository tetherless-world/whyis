from whyis.test.api_test_case import ApiTestCase
import json

labelsData = """@prefix ex: <http://example.com>.
ex:manyLabels <http://www.w3.org/2004/02/skos/core#prefLabel> "skos prefLabel";
<http://schema.org/name> "schema name";
<http://www.w3.org/2000/01/rdf-schema#label> "rdfs label";
<http://purl.org/dc/terms/title> "dc title";
<http://xmlns.com/foaf/0.1/name> "foaf name".
ex:oneLabel <http://purl.org/dc/terms/title> "dc title".
ex:noLabels ex:irrelevantProperty "irrelevant property"."""

labelsUris = ["http://example.com/manyLabels","http://example.com/oneLabel","http://example.com/noLabels"]
labelsExpected = ['skos prefLabel', 'dc title', 'noLabels']


class TestLabelsJsonView(ApiTestCase):
    def test_labels_view_home(self):
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

  def test_labels_view_entities(self):
    self.login_new_user()
    self.post_nanopub(data = labelsData, content_type="text/turtle")

    response = self.client.get("/?view=labels&uris="+','.join(quote_plus(uri) for uri in labelsUris))
    for i in range(len(labelsUris)):
      self.assertEquals(response.json[labelsUris[i]], labelsExpected[i])

