from whyis.test.api_test_case import ApiTestCase
import json

#prefix owl: <http://www.w3.org/2002/07/owl#>

prefices = """prefix ex: <http://example.org/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix owl: <http://www.w3.org/2002/07/owl#>
"""

testdata = ["""ex:someSubclass1 a owl:Class; rdfs:subClassOf [
	a owl:Restriction;
	owl:onProperty ex:someProperty;
    owl:someValuesFrom ex:someRange
].
ex:someProperty a ex:somePropertyType.""",
"""ex:someSubclass2 a owl:Class; rdfs:subClassOf [
	a owl:Restriction;
	owl:onDataRange ex:someDataRange;
	owl:onProperty ex:someProperty;
	owl:minQualifiedCardinality 5
].""",
"""ex:someSubclass3 a owl:Class; rdfs:subClassOf [
	a owl:Restriction;
	owl:onClass ex:someClass;
	owl:onProperty ex:someProperty;
	owl:maxQualifiedCardinality 5
].""",
"""ex:someSubclass4 a owl:Class; rdfs:subClassOf [
	a owl:Restriction;
	owl:onProperty ex:someProperty;
	owl:exactCardinality 5
].""",
"""ex:someSubclass5 a owl:Class; rdfs:subClassOf ex:someClass.
ex:someProperty a ex:somePropertyType; rdfs:domain ex:someClass; rdfs:range ex:someRange."""
]

class TestClassConstraints(ApiTestCase):

  def test_value_constraint(self):
    self.login_new_user()
    self.post_nanopub(data=prefices+testdata[0],
                      content_type="text/turtle")

    content = self.get_view(uri="http://example.org/someSubclass1",
                            view="constraints",
                            expected_template="class_constraints.json",
                            mime_type="application/json")

    json_content = json.loads(str(content.data, 'utf8'))
    self.assertEquals(len(json_content), 1)
    self.assertEquals(json_content[0]['class'], 'http://example.org/someSubclass1')
    self.assertEquals(json_content[0]['property'], 'http://example.org/someProperty')
    self.assertEquals(json_content[0]['propertyType'], 'http://example.org/somePropertyType')
    self.assertEquals(json_content[0]['extent'], 'http://www.w3.org/2002/07/owl#someValuesFrom')
    self.assertEquals(json_content[0]['range'], 'http://example.org/someRange')

  def test_data_range_constraint(self):
    self.login_new_user()
    self.post_nanopub(data=prefices+testdata[1],
                      content_type="text/turtle")

    content = self.get_view(uri="http://example.org/someSubclass2",
                            view="constraints",
                            expected_template="class_constraints.json",
                            mime_type="application/json")

    json_content = json.loads(str(content.data, 'utf8'))
    self.assertEquals(len(json_content), 1)
    self.assertEquals(json_content[0]['class'], 'http://example.org/someSubclass2')
    self.assertEquals(json_content[0]['property'], 'http://example.org/someProperty')
    self.assertEquals(json_content[0]['propertyType'], 'http://www.w3.org/2002/07/owl#DatatypeProperty')
    self.assertEquals(json_content[0]['extent'], 'http://www.w3.org/2002/07/owl#minQualifiedCardinality')
    self.assertEquals(json_content[0]['range'], 'http://example.org/someDataRange')
    self.assertEquals(json_content[0]['cardinality'], '5')


  def test_class_cardinality_constraint(self):
    self.login_new_user()
    self.post_nanopub(data=prefices+testdata[2],
                      content_type="text/turtle")

    content = self.get_view(uri="http://example.org/someSubclass3",
                            view="constraints",
                            expected_template="class_constraints.json",
                            mime_type="application/json")

    json_content = json.loads(str(content.data, 'utf8'))
    self.assertEquals(len(json_content), 1)
    self.assertEquals(json_content[0]['class'], 'http://example.org/someSubclass3')
    self.assertEquals(json_content[0]['property'], 'http://example.org/someProperty')
    self.assertEquals(json_content[0]['propertyType'], 'http://www.w3.org/2002/07/owl#ObjectProperty')
    self.assertEquals(json_content[0]['extent'], 'http://www.w3.org/2002/07/owl#maxQualifiedCardinality')
    self.assertEquals(json_content[0]['range'], 'http://example.org/someClass')
    self.assertEquals(json_content[0]['cardinality'], '5')

  def test_unqualified_cardinality_constraint(self):
    self.login_new_user()
    self.post_nanopub(data=prefices+testdata[3],
                      content_type="text/turtle")

    content = self.get_view(uri="http://example.org/someSubclass4",
                            view="constraints",
                            expected_template="class_constraints.json",
                            mime_type="application/json")

    json_content = json.loads(str(content.data, 'utf8'))
    self.assertEquals(len(json_content), 1)
    self.assertEquals(json_content[0]['class'], 'http://example.org/someSubclass4')
    self.assertEquals(json_content[0]['property'], 'http://example.org/someProperty')
    self.assertEquals(json_content[0]['extent'], 'http://www.w3.org/2002/07/owl#exactCardinality')
    self.assertEquals(json_content[0]['cardinality'], '5')

  def test_rdfs_domain_constraint(self):
    self.login_new_user()
    self.post_nanopub(data=prefices+testdata[4],
                      content_type="text/turtle")

    content = self.get_view(uri="http://example.org/someSubclass5",
                            view="constraints",
                            expected_template="class_constraints.json",
                            mime_type="application/json")

    json_content = json.loads(str(content.data, 'utf8'))
    print(json_content)
    self.assertEquals(len(json_content), 1)
    self.assertEquals(json_content[0]['class'], 'http://example.org/someSubclass5')
    self.assertEquals(json_content[0]['property'], 'http://example.org/someProperty')
    self.assertEquals(json_content[0]['propertyType'], 'http://example.org/somePropertyType')
    self.assertEquals(json_content[0]['range'], 'http://example.org/someRange')

