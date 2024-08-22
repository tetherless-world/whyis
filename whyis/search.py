import rdflib

latest_query = '''select distinct
?about
(max(?created) as ?updated)
#(group_concat(distinct ?type; separator="||") as ?types)
where {
    hint:Query hint:optimizer "Runtime" .                                                                                              graph ?np {
    ?np
        np:hasPublicationInfo ?pubinfo;
        np:hasAssertion ?assertion.
  }
  graph ?pubinfo {
      ?assertion dc:created|dc:modified ?created.
  }
    {
      graph ?np {
        ?np sio:isAbout|sio:SIO_000332 ?about.
      }
    }

    filter not exists {
      [] ?about [].
    }
#    optional {
#      ?about a ?type.
#    }

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
        #entity = g.get_resource(rdflib.URIRef(entry['about']), retrieve=False)
        #if 'label' not in entities[entry['about']]:
        #    entry['label'] = g.get_label(entity)
        #if 'description' not in entities[entry['about']]:
        #    d = [y for x,y in g.get_summary(entity)]
        #    if len(d) > 0:
        #        entry['description'] = d[0]
        #if entities[entry['about']] == entry or 'types' not in entities[entry['about']] or len(entities[entry['about']]['types']) == 0:
        #    entities[entry['about']]['types'] = [g.labelize(dict(uri=x),'uri','label')
        #                                         for x in entry['types'].split('||') if len(x) > 0]
    return results
