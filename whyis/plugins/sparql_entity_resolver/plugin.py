from whyis.plugin import Plugin, EntityResolverListener
import rdflib
from flask import current_app


prefixes = dict(
    skos = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#"),
    foaf = rdflib.URIRef("http://xmlns.com/foaf/0.1/"),
    text = rdflib.URIRef("http://jena.apache.org/fulltext#"),
    schema = rdflib.URIRef("http://schema.org/"),
    owl = rdflib.OWL,
    rdfs = rdflib.RDFS,
    rdf = rdflib.RDF,
    dc = rdflib.URIRef("http://purl.org/dc/terms/")
)

class SPARQLEntityResolver(EntityResolverListener):

    context_query="""
  optional {
    (?context ?cr) text:search ('''%s''' 100 0.4).
    ?node ?p ?context.
  }
"""
    type_query = """
?node rdf:type <%s> .
"""

    query = """
select distinct
?node
?label
(group_concat(distinct ?type; separator="||") as ?types)
(coalesce(?relevance+?cr, ?relevance) as ?score)
where {
  (?label ?relevance) text:search '''%s'''.
  ?node dc:title|rdfs:label|skos:prefLabel|skos:altLabel|foaf:name|dc:identifier|schema:name|skos:notation ?label.
  %s
  optional {
    ?node rdf:type ?type.
  }

  %s

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
  # filter not exists {
  #   ?node a owl:ObjectProperty.
  # }
  # filter not exists {
  #   ?node a owl:DatatypeProperty.
  # }
  filter not exists {
    ?node a <http://www.nanopub.org/nschema#PublicationInfo>
  }
} group by ?node ?label ?score ?cr ?relevance order by desc(?score) limit 10"""

    def __init__(self, database="knowledge"):
        self.database = database

    def on_resolve(self, term, type=None, context=None, label=True):
        graph = current_app.databases[self.database]
        context_query = ''
        if context is not None:
            context_query = self.context_query % context

        type_query = ''
        if type is not None:
             type_query = self.type_query% type

        query =  self.query % (term, type_query, context_query)
        #print(query)
        results = []
        for hit in graph.query(query, initNs=prefixes):
            result = hit.asdict()
            result['types'] = [{'uri':x} for x in result.get('types','').split('||')]
            if label:
                current_app.labelize(result,'node','preflabel')
                result['types'] = [
                    current_app.labelize(x,'uri','label')
                    for x in result['types']
                ]
            results.append(result)
        return results


class SPARQLEntityResolverPlugin(Plugin):

    resolvers = {
        "sparql" : SPARQLEntityResolver,
        "fuseki" : SPARQLEntityResolver
    }

    def init(self):
        resolver_type = self.app.config.get('RESOLVER_TYPE', 'fuseki')
        resolver_db = self.app.config.get('RESOLVER_DB', "knowledge")
        resolver = self.resolvers[resolver_type](resolver_db)
        self.app.add_listener(resolver)
