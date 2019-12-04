

summaryPropertyValues = {
  'http://www.w3.org/2008/05/skos##definition'  : 'skos definition',
  'https://schema.org/description'              : 'schema description',
  'http://purl.org/dc/terms/abstract'           : 'dc abstract', 
  'http://purl.org/dc/terms/description'        : 'dc description',
  'http://purl.org/dc/terms/summary'            : 'dc summary',
  'http://www.w3.org/2000/01/rdf-schema#comment': 'rdfs comment',
  'http://purl.org/dc/elements/1.1/description' : 'dcelements description',
  'http://purl.obolibrary.org/obo/IAO_0000115'  : 'obo iao 0000115',
  'http://www.w3.org/ns/prov#value'             : 'prov value',
  'http://semanticscience.org/resource/'        : 'sio hasValue'
}

uriAll = 'http://example.com/summaryTest1'
dataAll = """<http://example.com/summaryTest1> skos:definition "skos definition";
              schema:description "schema description";
			  dc:abstract "dc abstract";
			  dc:description "dc description";
			  dc:summary "dc summary";
			  rdfs:comment "rdfs comment";
			  dcelements:description "dcelements description";
			  <http://purl.obolibrary.org/obo/IAO_0000115> "obo iao 0000115";
			  prov:value "prov value";
			  sio:hasValue "sio hasValue";
        <http://example.com/irrelevantProperty> "irrelevant property"."""

uriNone = 'http://example.com/summaryTest2'
dataNone = '<http://example.com/summaryTest2> <http://example.com/irrelevantProperty> "irrelevant property".'

uriCustom = 'http://example.com/summaryTest1'
dataCustom = '<http://example.com/summaryTest3> <http://example.com/summaryTestProperty> "custom property".'


class TestResourceSummary(ApiTestCase):
  def test_summary_all(self):
    self.login_new_user()
    self.post_nanopub(data = dataAll, content_type="text/turtle")
    
    response = self.client.get("/?view=summary&uri="+urlencode(uriAll))
    for property in summaryPropertyValues:
      self.assertIn(property, response.json)
      self.assertEquals(response.json[property], summaryPropertyValues[property])
      
    self.assertNotIn('http://example.com/irrelevantProperty'), response.json
    
  def test_summary_none(self):   
    self.login_new_user()
    self.post_nanopub(data = dataNone, content_type="text/turtle")
    
    response = self.client.get("/?view=summary&uri="+urlencode(uriNone))
    self.assertEquals(len(response.json), 0)