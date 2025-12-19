from whyis.plugin import Plugin, EntityResolverListener, PluginBlueprint
import rdflib
from flask import current_app


prefixes = dict(
    skos = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#"),
    foaf = rdflib.URIRef("http://xmlns.com/foaf/0.1/"),
    fts = rdflib.URIRef("http://aws.amazon.com/neptune/vocab/v01/services/fts#"),
    schema = rdflib.URIRef("http://schema.org/"),
    owl = rdflib.OWL,
    rdfs = rdflib.RDFS,
    rdf = rdflib.RDF,
    dc = rdflib.URIRef("http://purl.org/dc/terms/")
)


class NeptuneEntityResolver(EntityResolverListener):
    """
    Entity resolver for AWS Neptune with OpenSearch full-text search integration.
    Uses the Neptune fts:search predicate for full-text queries.
    """

    context_query="""
  optional {
    ?context fts:search '%s' .
    ?context fts:score ?cr .
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
  ?label fts:search '%s' .
  ?label fts:score ?relevance .
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


class NeptuneSearchPlugin(Plugin):

    resolvers = {
        "neptune" : NeptuneEntityResolver
    }

    def create_blueprint(self):
        blueprint = PluginBlueprint('neptune_search', __name__, template_folder='templates')
        return blueprint

    def init(self):
        resolver_type = self.app.config.get('RESOLVER_TYPE', 'fuseki')
        resolver_db = self.app.config.get('RESOLVER_DB', "knowledge")
        if resolver_type in self.resolvers:
            resolver = self.resolvers[resolver_type](resolver_db)
            self.app.add_listener(resolver)
