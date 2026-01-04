from whyis.plugin import Plugin, EntityResolverListener
from whyis.namespace import NS
import rdflib
from flask import current_app
from flask_pluginengine import PluginBlueprint, current_plugin
from rdflib import URIRef
from rdflib.graph import ConjunctiveGraph
import requests
import logging
import os
from aws_requests_auth.aws_auth import AWSRequestsAuth

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
            # Escape the type URI to prevent SPARQL injection
            escaped_type = self._escape_sparql_string(type)
            type_query = self.type_query % escaped_type

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
    
    Uses WhyisSPARQLUpdateStore with a custom requests session for AWS SigV4 auth.
    
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
    from urllib.parse import urlparse
    
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    
    # Get AWS region (required for Neptune)
    region_name = config.get("_region")
    if not region_name:
        raise ValueError("Neptune driver requires '_region' configuration parameter")
    
    service_name = config.get("_service_name", "neptune-db")
    endpoint_url = config["_endpoint"]
    
    # Extract host from endpoint URL for AWS auth
    parsed_url = urlparse(endpoint_url)
    aws_host = parsed_url.netloc
    
    # Create AWS authentication using environment credentials
    # Credentials will be automatically picked up from environment variables or ~/.aws/credentials
    aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
    
    if not aws_access_key or not aws_secret_key:
        raise ValueError("Neptune driver requires AWS credentials (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables)")
    
    auth = AWSRequestsAuth(
        aws_access_key=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        aws_host=aws_host,
        aws_region=region_name,
        aws_service=service_name,
        aws_token=aws_session_token
    )
    
    # Create custom requests session with AWS auth
    session = requests.Session()
    session.auth = auth
    
    # Create store with standard WhyisSPARQLUpdateStore, passing custom session
    store = WhyisSPARQLUpdateStore(
        query_endpoint=endpoint_url,
        update_endpoint=endpoint_url,
        method="POST",
        returnFormat='json',
        node_to_sparql=node_to_sparql,
        custom_requests=session  # Pass custom session directly
    )
    
    store.query_endpoint = endpoint_url
    store.gsp_endpoint = config.get("_gsp_endpoint", endpoint_url)
    store.auth = None  # Neptune uses AWS SigV4, not basic auth
    
    # Add GSP protocol methods with AWS authentication
    store = _remote_sparql_store_protocol_with_aws(store, auth)
    
    graph = ConjunctiveGraph(store, defaultgraph)
    return graph

def _remote_sparql_store_protocol_with_aws(store, aws_auth):
    """
    Add Graph Store Protocol (GSP) operations with AWS authentication.
    
    This is similar to _remote_sparql_store_protocol but uses AWS SigV4 auth
    instead of basic auth.
    
    Args:
        store: A SPARQL store object with gsp_endpoint attribute
        aws_auth: AWSRequestsAuth object for request signing
        
    Returns:
        The store object with GSP methods attached
    """
    # Create a reusable session with AWS auth for all GSP operations
    session = requests.Session()
    session.auth = aws_auth
    session.keep_alive = False
    
    def publish(data, format='text/trig;charset=utf-8'):
        kwargs = dict(
            headers={'Content-Type': format},
        )
        r = session.post(store.gsp_endpoint, data=data, **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")

    def put(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='turtle')
        
        kwargs = dict(
            headers={'Content-Type': 'text/turtle;charset=utf-8'},
        )
        r = session.put(store.gsp_endpoint,
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
        
        kwargs = dict(
            headers={'Content-Type': 'text/trig;charset=utf-8'},
        )
        r = session.post(store.gsp_endpoint, data=data, **kwargs)
        if not r.ok:
            logger.error(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")

    def delete(c):
        kwargs = dict()
        r = session.delete(store.gsp_endpoint,
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
