from ..api_test_data import PERSON_INSTANCE_TURTLE
from whyis.test.api_test_case import ApiTestCase
import json

some_nanopub="""@prefix : <http://www.example.org/whyis#> .
@prefix np:  <http://www.nanopub.org/nschema#> .
@prefix sio: <http://semanticscience.org/resource/> .

    :npTest a np:Nanopublication .
    :npTest np:hasAssertion :assertion .
    :npTest np:hasProvenance :provenance .
    :npTest np:hasPublicationInfo :pubInfo .

:npTest {
    :npTest sio:isAbout :JaneDoe .
}

:assertion {
    :JaneDoe <http://schema.org/name> "Jane Doe".
    :assertion a np:Assertion .
}

:provenance {
    :provenance a np:Provenance .
}

:pubInfo {
    :pubInfo a np:PublicationInfo .
    :assertion <http://purl.org/dc/elements/1.1/created> "Something" .
}"""

class TestLatestJsonView(ApiTestCase):
    def test(self):
        try:
            import config
        except:
            from whyis import config_defaults as config
        
        HOME_INSTANCE_URI = config.LOD_PREFIX + "/Home"

        self.login_new_user()

        self.post_nanopub(data=some_nanopub,
                          content_type="application/trig")

        content = self.get_view(uri=HOME_INSTANCE_URI,
                                view="latest",
                                expected_template="latest.json",
                                mime_type="application/json",
                                )

        json_content = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(json_content, list)
#        self.assertEquals(len(json_content), 0)
        print(json_content)
        print(content)
