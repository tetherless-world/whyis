import json

from whyis.test.api_test_case import ApiTestCase

from ..api_test_data import ONTOLOGY_INSTANCE_TURTLE


class TestDescribeOntology(ApiTestCase):
    def test_describe_ontology(self):
        self.login_new_user()
        ontology = ONTOLOGY_INSTANCE_TURTLE

        self.post_nanopub(data=ontology,
                          content_type="text/turtle")

        content = self.get_view(uri="http://example.com/",
                                view="describe",
                                mime_type="application/json",
                                expected_template="describe_ontology.json")

        data = json.loads(str(content.data, 'utf8'))
        self.assertIsInstance(data, list, "'describe' view returned unexpected structure")
        self.assertTrue(data, "'describe' view returned empty list")
        self.assertIn("@graph", data[0], "'describe' view missing @graph key")
        self.assertIn("@id", data[0], "'describe' view missing @id key for graph")

        graph = data[0]["@graph"]
        self.assertEqual(len(graph), 2, "'describe' view returned the wrong number of subjects")

        for subject in graph:
            if subject["@id"] == "http://example.com/":
                self.assertEqual(len(subject.keys()), 2,
                                 "Subject in 'describe' view has unexpected number of predicates")
                self.assertIn("http://www.w3.org/2002/07/owl#Ontology", subject["@type"],
                              "Expected an ontology type object in the 'describe' view")
            elif subject["@id"] == "http://example.com/janedoe":
                self.assertEqual(len(subject.keys()), 6,
                                 "Subject in 'describe' view has unexpected number of predicates")
