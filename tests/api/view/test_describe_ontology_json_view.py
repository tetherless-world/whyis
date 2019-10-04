import json

from whyis.test.api_test_case import ApiTestCase

from ..api_test_data import ONTOLOGY_INSTANCE_TURTLE, ONTOLOGY_INSTANCE_URI


class TestDescribeOntologyJsonView(ApiTestCase):
    def test(self):
        self.login_new_user()
        ontology = ONTOLOGY_INSTANCE_TURTLE

        self.post_nanopub(data=ontology,
                          content_type="text/turtle")

        content = self.get_view(uri=ONTOLOGY_INSTANCE_URI,
                                view="describe",
                                mime_type="application/json",
                                expected_template="describe_ontology.json")

        data = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(data, list, "'describe' view returned unexpected structure")
        self.assertTrue(data, "'describe' view returned empty list")
        self.assertIn("@graph", data[0], "'describe' view missing @graph key")
        self.assertIn("@id", data[0], "'describe' view missing @id key for graph")

        graph = data[0]["@graph"]
        self.assertEqual(len(graph), 1, "'describe' view returned the wrong number of subjects")

        for subject in graph:
            if subject["@id"] == ONTOLOGY_INSTANCE_URI:
                self.assertEqual(len(subject.keys()), 2,
                                 "Subject in 'describe' view has unexpected number of predicates")
                self.assertIn("http://www.w3.org/2002/07/owl#Ontology", subject["@type"],
                              "Expected an ontology type object in the 'describe' view")
