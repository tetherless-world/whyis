import rdflib

prefixes = dict(
    skos = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#"),
    foaf = rdflib.URIRef("http://xmlns.com/foaf/0.1/"),
    bds = rdflib.URIRef("http://www.bigdata.com/rdf/search#"),
    dc = rdflib.URIRef("http://purl.org/dc/terms/")
        )

def resolve(graph, g, term, context=None):
    context_query = ''
    if context is not None:
        context_query = """
  optional {
    ?node ?p ?context.
    ?context bds:search '''%s''';
         bds:matchAllTerms "false";
		 bds:relevance ?cr ;
         bds:minRelevance 0.4.
  }
""" % context
        
    query = """
select distinct
?node
?label
(group_concat(distinct ?type; separator="||") as ?types)
(coalesce(?relevance+?cr, ?relevance) as ?score)
where {
  ?node dc:title|rdfs:label|skos:prefLabel|skos:altLabel|foaf:name ?label.
  ?label bds:search '''%s''';
         bds:matchAllTerms "false";
		 bds:relevance ?relevance .
  
  ?node dc:title|rdfs:label|skos:prefLabel|skos:altLabel|foaf:name ?label.
  
  optional {
    ?node rdf:type/rdfs:subClassOf* ?type.
  }

  %s
  
  filter not exists {
    [] ?node [].
  }
  filter not exists {
    ?node a <http://semanticscience.org/resource/Term>
  }
  filter not exists {
    ?node a <http://www.nanopub.org/nschema#Nanopublication>
  }
  filter not exists {
    ?node a <http://www.nanopub.org/nschema#Assertion>
  }
  filter not exists {
    ?node a <http://www.nanopub.org/nschema#Provenance>
  }
  filter not exists {
    ?node a <http://www.nanopub.org/nschema#PublicationInfo>
  }
} group by ?node ?label ?score ?cr ?relevance order by desc(?score) limit 10""" % (term, context_query)
    print query
    results = []
    for hit in graph.query(query, initNs=prefixes):
        result = hit.asdict()
        g.labelize(result,'node','preflabel')
        result['types'] = [g.labelize({'uri':x},'uri','label') for x in result['types'].split('||')]
        results.append(result)
    return results
