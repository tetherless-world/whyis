from whyis.plugin import Plugin, EntityResolverListener
from whyis.namespace import NS
import rdflib
from flask import current_app
from flask_pluginengine import PluginBlueprint, current_plugin


prefixes = dict(
    skos = rdflib.URIRef("http://www.w3.org/2004/02/skos/core#"),
    foaf = rdflib.URIRef("http://xmlns.com/foaf/0.1/"),
    text = rdflib.URIRef("http://jena.apache.org/fulltext#"),
    schema = rdflib.URIRef("http://schema.org/"),
    owl = rdflib.OWL,
    rdfs = rdflib.RDFS,
    rdf = rdflib.RDF,
    dc = rdflib.URIRef("http://purl.org/dc/terms/"),
    fts = rdflib.URIRef('http://aws.amazon.com/neptune/vocab/v01/services/fts#')
)

class NeptuneEntityResolver(EntityResolverListener):

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
(0.9 as ?score)
where {
    SERVICE fts:search {
        fts:config neptune-fts:query '''%s''' .
        fts:config neptune-fts:endpoint '%s' .
        fts:config neptune-fts:queryType 'match' .
        fts:config neptune-fts:field dc:title .
        fts:config neptune-fts:field rdfs:label .
        fts:config neptune-fts:field skos:prefLabel .
        fts:config neptune-fts:field skos:altLabel .
        fts:config neptune-fts:field foaf:name .
        fts:config neptune-fts:field dc:identifier .
        fts:config neptune-fts:field schema:name .
        fts:config neptune-fts:field skos:notation .
        fts:config neptune-fts:return ?node .
  }

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
} group by ?node ?label limit 10"""

    def __init__(self, database="knowledge"):
        self.database = database

    def on_resolve(self, term, type=None, context=None, label=True):
        print(f'Searching {self.database} for {term}')
        graph = current_app.databases[self.database]
        fts_endpoint = current_app.config['NEPTUNE_FTS_ENDPOINT']
        #context_query = ''
        #if context is not None:
        #    context_query = self.context_query % context

        type_query = ''
        if type is not None:
             type_query = self.type_query% type

        query =  self.query % (term, fts_endpoint, type_query)
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

plugin_blueprint = PluginBlueprint('neptune', __name__)

class NeptuneSearchPlugin(Plugin):

    resolvers = {
        "neptune" : NeptuneEntityResolver
    }

    def create_blueprint(self):
        return plugin_blueprint
    
    def init(self):
        NS.fts = rdflib.Namespace('http://aws.amazon.com/neptune/vocab/v01/services/fts#')
        resolver_type = self.app.config.get('RESOLVER_TYPE', 'neptune')
        resolver_db = self.app.config.get('RESOLVER_DB', "knowledge")
        resolver = self.resolvers[resolver_type](resolver_db)
        self.app.add_listener(resolver)
