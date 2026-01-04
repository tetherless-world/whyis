from whyis.plugin import Plugin, EntityResolverListener
from whyis.namespace import NS
import rdflib
from flask import current_app
from flask_pluginengine import PluginBlueprint, current_plugin
from rdflib import URIRef
from rdflib.graph import ConjunctiveGraph
import requests
import logging
import boto3
from requests_aws4auth import AWS4Auth

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
    SERVICE <http://aws.amazon.com/neptune/vocab/v01/services/fts#search> {
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#query> "%s" .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#endpoint> "%s" .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#queryType> "match" .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> dc:title .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> rdfs:label .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> skos:prefLabel .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> skos:altLabel .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> foaf:name .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> dc:identifier .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> schema:name .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#field> skos:notation .
        <http://aws.amazon.com/neptune/vocab/v01/services/fts#config> <http://aws.amazon.com/neptune/vocab/v01/services/fts#return> ?node .
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
    
    def _escape_sparql_string(self, s):
        """
        Escape a string for safe inclusion in a SPARQL query.
        
        This prevents SPARQL injection by escaping special characters.
        """
        if s is None:
            return ""
        # Escape backslashes first, then quotes, then newlines/returns
        s = str(s).replace('\\', '\\\\')
        s = s.replace('"', '\\"')
        s = s.replace('\n', '\\n')
        s = s.replace('\r', '\\r')
        return s

    def on_resolve(self, term, type=None, context=None, label=True):
        logger.info(f'Searching {self.database} for {term}')
        graph = current_app.databases[self.database]
        fts_endpoint = current_app.config['neptune_fts_endpoint']
        
        # Safely escape the search term for inclusion in SPARQL query
        escaped_term = self._escape_sparql_string(term)
        escaped_endpoint = self._escape_sparql_string(fts_endpoint)
        
        type_query = ''
        if type is not None:
             type_query = self.type_query % type

        query = self.query % (escaped_term, escaped_endpoint, type_query)
        
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
    
    This driver follows the same pattern as sparql_driver but adds AWS IAM authentication
    using SigV4 request signing for both SPARQL operations and GSP operations.
    
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
    from whyis.database.database_utils import node_to_sparql, WhyisSPARQLUpdateStore
    
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    
    # Get AWS region (required for Neptune)
    region_name = config.get("_region")
    if not region_name:
        raise ValueError("Neptune driver requires '_region' configuration parameter")
    
    service_name = config.get("_service_name", "neptune-db")
    
    # Create AWS authenticated session for GSP operations
    credentials = boto3.Session().get_credentials()
    aws_auth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region_name,
        service_name,
        session_token=credentials.token
    )
    
    # Create store with standard WhyisSPARQLUpdateStore
    kwargs = dict(
        query_endpoint=config["_endpoint"],
        update_endpoint=config["_endpoint"],
        method="POST",
        returnFormat='json',
        node_to_sparql=node_to_sparql
    )
    
    store = WhyisSPARQLUpdateStore(**kwargs)
    store.query_endpoint = config["_endpoint"]
    store.gsp_endpoint = config.get("_gsp_endpoint", config["_endpoint"])
    store.auth = None  # Neptune uses AWS SigV4, not basic auth
    
    # Monkey-patch the store's connector to use AWS authentication
    _inject_neptune_auth(store, aws_auth)
    
    # Add GSP protocol methods compatible with sparql_driver but with AWS auth
    store = _remote_sparql_store_protocol_with_aws(store, aws_auth)
    
    graph = ConjunctiveGraph(store, defaultgraph)
    return graph


def _inject_neptune_auth(store, aws_auth):
    """
    Inject AWS authentication into the SPARQL store's query method.
    
    This monkey-patches the store's query and update methods to use requests with AWS auth
    instead of rdflib's default urllib-based implementation.
    
    Args:
        store: The SPARQL store object
        aws_auth: AWS4Auth object for request signing
    """
    original_query = store.query
    
    def query_with_aws_auth(query_str, *args, **kwargs):
        """Execute SPARQL query with AWS IAM authentication."""
        session = requests.Session()
        session.auth = aws_auth
        
        params = {}
        default_graph = kwargs.get('default_graph')
        if default_graph:
            params["default-graph-uri"] = default_graph
            
        headers = {"Accept": store.response_mime_types()}
        
        if store.method == "POST":
            headers["Content-Type"] = "application/sparql-query"
            response = session.post(
                store.query_endpoint,
                params=params,
                data=query_str.encode('utf-8'),
                headers=headers
            )
        else:
            params["query"] = query_str
            response = session.get(
                store.query_endpoint,
                params=params,
                headers=headers
            )
        
        response.raise_for_status()
        
        # Return the response in the format rdflib expects
        from rdflib.plugins.stores.sparqlconnector import SPARQLConnector, Result
        from io import BytesIO
        return Result((response.status_code, response.reason), response.headers.get('content-type'), BytesIO(response.content))
    
    store.query = query_with_aws_auth


def _remote_sparql_store_protocol_with_aws(store, aws_auth):
    """
    Add Graph Store Protocol (GSP) operations with AWS authentication.
    
    This is similar to _remote_sparql_store_protocol but uses AWS SigV4 auth
    instead of basic auth.
    
    Args:
        store: A SPARQL store object with gsp_endpoint attribute
        aws_auth: AWS4Auth object for request signing
        
    Returns:
        The store object with GSP methods attached
    """
    def publish(data, format='text/trig;charset=utf-8'):
        s = requests.Session()
        s.auth = aws_auth
        s.keep_alive = False
        
        kwargs = dict(
            headers={'Content-Type': format},
        )
        r = s.post(store.gsp_endpoint, data=data, **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")

    def put(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='turtle')
        s = requests.Session()
        s.auth = aws_auth
        s.keep_alive = False
        
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

    def post(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='trig')
        s = requests.Session()
        s.auth = aws_auth
        s.keep_alive = False
        
        kwargs = dict(
            headers={'Content-Type': 'text/trig;charset=utf-8'},
        )
        r = s.post(store.gsp_endpoint, data=data, **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")

    def delete(c):
        s = requests.Session()
        s.auth = aws_auth
        s.keep_alive = False
        
        kwargs = dict()
        r = s.delete(store.gsp_endpoint,
                     params=dict(graph=c),
                     **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} DELETE returned status {r.status_code}:\n{r.text}")

    store.publish = publish
    store.put = put
    store.post = post
    store.delete = delete
    
    return store


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
