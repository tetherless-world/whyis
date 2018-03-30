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
    ?node a owl:AnnotationProperty.
  }
  filter not exists {
    ?node a owl:ObjectProperty.
  }
  filter not exists {
    ?node a owl:DatatypeProperty.
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

latest_query = '''select distinct 
?about 
(max(coalesce(?modified, ?created)) as ?updated) 
(group_concat(distinct ?type; separator="||") as ?types)
where {                                                                                                 
  graph ?np {
    ?np 
        np:hasPublicationInfo ?pubinfo;
        np:hasAssertion ?assertion.
  }
  graph ?pubinfo {
    optional {
      ?assertion dc:created ?created.
    }
    optional {
      ?assertion dc:modified ?modified.
    }
  }
    {
      graph ?np { 
        ?np sio:isAbout ?about.
      }
    } union {
	  graph ?assertion {
        ?about ?p ?o.
        filter (!regex(str(?about), "^bnode:"))
        filter not exists {
          [] ?relation <http://purl.org/twc/vocab/setl/SemanticETLScript>.
        }
      }
      ?about a [].
    }
  
    filter not exists {
      [] ?about [].
    }

    
    optional {
      ?about rdf:type/rdfs:subClassOf* ?type.
    }
    
} group by ?about order by desc (?updated)
LIMIT 20
'''

def latest(graph, g):
    results = []
    entities = {}
    for row in graph.query(latest_query, initNs=g.ns.prefixes):
        entry = row.asdict()
        if entry['about'] not in entities:
            entities[entry['about']] = entry
            results.append(entry)
        entity = g.get_resource(rdflib.URIRef(entry['about']), retrieve=False)
        if 'label' not in entities[entry['about']]:
            entry['label'] = g.get_label(entity)
        if 'description' not in entities[entry['about']]:
            d = [y for x,y in g.get_summary(entity)]
            if len(d) > 0:
                entry['description'] = d[0]
        if entities[entry['about']] == entry or 'types' not in entities[entry['about']] or len(entities[entry['about']]['types']) == 0:
            entities[entry['about']]['types'] = [g.labelize(dict(uri=x),'uri','label')
                                                 for x in entry['types'].split('||') if len(x) > 0]
    return results
                                
