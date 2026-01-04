from whyis.plugin import Plugin, EntityResolverListener
from whyis.namespace import NS
import rdflib
from flask import current_app
from flask_pluginengine import PluginBlueprint, current_plugin
from rdflib import URIRef
from rdflib.graph import ConjunctiveGraph
import requests
import logging

# Import the Neptune store classes from this plugin
from .neptune_sparql_store import NeptuneSPARQLStore, NeptuneSPARQLUpdateStore

logger = logging.getLogger(__name__)


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
        fts_endpoint = current_app.config['neptune_fts_endpoint']
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


def neptune_driver(config):
    """
    Create an AWS Neptune SPARQL-based RDF graph store with IAM authentication.
    
    This driver extends the sparql_driver to support AWS IAM authentication using
    SigV4 request signing. It's designed specifically for Amazon Neptune databases.
    
    Configuration options (via Flask config with prefix like KNOWLEDGE_ or ADMIN_):
    - _endpoint: Neptune SPARQL query/update endpoint (required)
    - _gsp_endpoint: Graph Store Protocol endpoint (optional, defaults to _endpoint)
    - _region: AWS region where Neptune instance is located (required)
    - _service_name: AWS service name for signing (optional, default: 'neptune-db')
    - _default_graph: Default graph URI (optional)
    
    Example configuration in system.conf:
        KNOWLEDGE_ENDPOINT = 'https://my-neptune.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/sparql'
        KNOWLEDGE_REGION = 'us-east-1'
        KNOWLEDGE_GSP_ENDPOINT = 'https://my-neptune.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/data'
    
    Authentication:
        Uses AWS credentials from the environment (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        or IAM roles. All requests are signed with SigV4, including full text search queries.
    """
    from whyis.database.database_utils import node_to_sparql, _remote_sparql_store_protocol
    
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    
    # Get AWS region (required for Neptune)
    region_name = config.get("_region")
    if not region_name:
        raise ValueError("Neptune driver requires '_region' configuration parameter")
    
    service_name = config.get("_service_name", "neptune-db")
    
    kwargs = dict(
        query_endpoint=config["_endpoint"],
        update_endpoint=config["_endpoint"],
        method="POST",
        returnFormat='json',
        node_to_sparql=node_to_sparql,
        region_name=region_name,
        service_name=service_name
    )
    
    # Create Neptune store with IAM authentication
    store = NeptuneSPARQLUpdateStore(**kwargs)
    store.query_endpoint = config["_endpoint"]
    # Set GSP endpoint: use _gsp_endpoint if provided, otherwise fall back to query_endpoint
    store.gsp_endpoint = config.get("_gsp_endpoint", config["_endpoint"])
    
    # For Neptune, we need to use AWS auth instead of basic auth
    store.auth = None  # Neptune uses AWS SigV4, not basic auth
    
    # Add GSP protocol methods with AWS authentication
    store = _remote_sparql_store_protocol(store)
    
    # Override the GSP methods to use AWS authentication
    # The store's connector already handles auth for SPARQL queries
    # We need to make sure GSP operations also use AWS auth
    _add_neptune_gsp_auth(store, region_name, service_name)
    
    graph = ConjunctiveGraph(store, defaultgraph)
    return graph


def _add_neptune_gsp_auth(store, region_name, service_name):
    """
    Add AWS IAM authentication to Graph Store Protocol operations.
    
    This function wraps the GSP methods (publish, put, post, delete) to add
    AWS SigV4 signing to their HTTP requests.
    
    Args:
        store: The Neptune store object
        region_name: AWS region name
        service_name: AWS service name for signing
    """
    import boto3
    from requests_aws4auth import AWS4Auth
    
    # Get AWS credentials
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region_name,
        service_name,
        session_token=credentials.token
    )
    
    # Wrap the original methods to add AWS auth
    original_publish = store.publish
    original_put = store.put
    original_post = store.post
    original_delete = store.delete
    
    def publish_with_auth(data, format='text/trig;charset=utf-8'):
        s = requests.session()
        s.keep_alive = False
        s.auth = aws_auth
        
        kwargs = dict(
            headers={'Content-Type': format},
        )
        r = s.post(store.gsp_endpoint, data=data, **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")
    
    def put_with_auth(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='turtle')
        s = requests.session()
        s.keep_alive = False
        s.auth = aws_auth
        
        kwargs = dict(
            headers={'Content-Type': 'text/turtle;charset=utf-8'},
        )
        r = s.put(store.gsp_endpoint,
                  params=dict(graph=graph.identifier),
                  data=data,
                  **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} PUT returned status {r.status_code}:\n{r.text}")
        else:
            logger.debug(f"{r.text} {r.status_code}")
    
    def post_with_auth(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='trig')
        s = requests.session()
        s.keep_alive = False
        s.auth = aws_auth
        
        kwargs = dict(
            headers={'Content-Type': 'text/trig;charset=utf-8'},
        )
        r = s.post(store.gsp_endpoint, data=data, **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")
    
    def delete_with_auth(c):
        s = requests.session()
        s.keep_alive = False
        s.auth = aws_auth
        
        kwargs = dict()
        r = s.delete(store.gsp_endpoint,
                     params=dict(graph=c),
                     **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} DELETE returned status {r.status_code}:\n{r.text}")
    
    # Replace methods with authenticated versions
    store.publish = publish_with_auth
    store.put = put_with_auth
    store.post = post_with_auth
    store.delete = delete_with_auth


def create_neptune_query_store(store):
    """
    Create a read-only query store from an existing Neptune store.
    
    This function creates a query-only store that can be used for read operations
    without update capabilities, while preserving AWS authentication.
    
    Args:
        store: The source Neptune store object
        
    Returns:
        A new Neptune store configured for queries only
    """
    from whyis.database.database_utils import node_to_sparql
    
    new_store = NeptuneSPARQLStore(
        endpoint=store.query_endpoint,
        query_endpoint=store.query_endpoint,
        region_name=store.region_name,
        service_name=getattr(store, 'service_name', 'neptune-db'),
        node_to_sparql=node_to_sparql
    )
    return new_store


class NeptuneSearchPlugin(Plugin):

    resolvers = {
        "neptune" : NeptuneEntityResolver
    }

    def create_blueprint(self):
        return plugin_blueprint
    
    def init(self):
        """
        Initialize the Neptune plugin.
        
        This registers the Neptune database driver and entity resolver.
        """
        # Import and register the Neptune driver
        from whyis.database.database_utils import driver, drivers
        
        # Register the Neptune driver
        if 'neptune' not in drivers:
            drivers['neptune'] = neptune_driver
        
        # Set up namespace
        NS.fts = rdflib.Namespace('http://aws.amazon.com/neptune/vocab/v01/services/fts#')
        
        # Set up entity resolver
        resolver_type = self.app.config.get('RESOLVER_TYPE', 'neptune')
        resolver_db = self.app.config.get('RESOLVER_DB', "knowledge")
        resolver = self.resolvers[resolver_type](resolver_db)
        self.app.add_listener(resolver)
