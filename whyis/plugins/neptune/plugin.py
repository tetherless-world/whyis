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
import uuid
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
        fts_endpoint = current_app.config['NEPTUNE_FTS_ENDPOINT']
        #context_query = ''
        
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
    
    Uses NeptuneBoto3Store with boto3 for credential management and AWS SigV4 auth.
    
    Configuration options (via Flask config with prefix like KNOWLEDGE_ or ADMIN_):
    - _endpoint: Neptune SPARQL query/update endpoint (required)
    - _gsp_endpoint: Graph Store Protocol endpoint (optional, defaults to _endpoint)
    - _region: AWS region where Neptune instance is located (required)
    - _service_name: AWS service name for signing (optional, default: 'neptune-db')
    - _default_graph: Default graph URI (optional)
    - _use_temp_graph: Use temporary UUID graphs for GSP operations (optional, default: True)
        When True, publish/put/post operations use a temporary UUID-based graph URI
        to ensure graph-aware semantics instead of using the default graph.
    - _use_instance_metadata: Use EC2 instance metadata for credentials (optional, default: True)
    
    Example configuration in system.conf:
        KNOWLEDGE_ENDPOINT = 'https://my-neptune.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/sparql'
        KNOWLEDGE_REGION = 'us-east-1'
        KNOWLEDGE_GSP_ENDPOINT = 'https://my-neptune.cluster-xxx.us-east-1.neptune.amazonaws.com:8182/data'
        KNOWLEDGE_USE_TEMP_GRAPH = True  # Default, ensures graph-aware semantics
    
    Authentication:
        Uses boto3 for AWS credential discovery (environment variables, IAM roles, 
        instance metadata, etc.). All requests are signed with SigV4, including 
        full text search queries.
    """
    from whyis.database.database_utils import node_to_sparql
    from whyis.plugins.neptune.neptune_boto3_store import NeptuneBoto3Store
    
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    
    # Get AWS region (required for Neptune)
    region_name = config.get("_region")
    if not region_name:
        raise ValueError("Neptune driver requires '_region' configuration parameter")
    
    service_name = config.get("_service_name", "neptune-db")
    endpoint_url = config["_endpoint"]
    
    # Get configuration options
    use_temp_graph = config.get("_use_temp_graph", True)
    use_instance_metadata = config.get("_use_instance_metadata", True)
    
    # Create store with NeptuneBoto3Store (uses boto3 for authentication)
    store = NeptuneBoto3Store(
        query_endpoint=endpoint_url,
        update_endpoint=endpoint_url,
        region_name=region_name,
        service_name=service_name,
        use_instance_metadata=use_instance_metadata,
        method="POST",
        returnFormat='json',
        node_to_sparql=node_to_sparql
    )
    
    # Set GSP endpoint
    store.gsp_endpoint = config.get("_gsp_endpoint", endpoint_url)
    
    # Add GSP protocol methods with boto3 authentication
    store = _add_gsp_methods_to_boto3_store(store, use_temp_graph=use_temp_graph)
    
    graph = ConjunctiveGraph(store, defaultgraph)
    return graph

def _add_gsp_methods_to_boto3_store(store, use_temp_graph=True):
    """
    Add Graph Store Protocol (GSP) operations to a NeptuneBoto3Store.
    
    This adds authenticated GSP methods (publish, put, post, delete) to the store
    using the store's built-in boto3 authentication via _request method.
    
    When use_temp_graph is True (default), publish/put/post operations use a
    temporary UUID-based graph URI to ensure graph-aware semantics. This prevents
    triples from being inserted into an explicit default graph and instead maintains
    the graph structure from the RDF data (e.g., TriG format).
    
    Args:
        store: A NeptuneBoto3Store object with gsp_endpoint attribute and _request method
        use_temp_graph: If True, use temporary UUID graphs for GSP operations (default: True)
        
    Returns:
        The store object with GSP methods attached
    """
    
    def publish(data, format='text/trig;charset=utf-8'):
        kwargs = dict(
            headers={'Content-Type': format},
        )
        
        if use_temp_graph:
            # Generate a temporary UUID-based graph URI
            temp_graph_uri = f"urn:uuid:{uuid.uuid4()}"
            
            # POST to the temporary graph using authenticated request
            params = dict(graph=temp_graph_uri)
            url = f"{store.gsp_endpoint}?graph={temp_graph_uri}"
            
            try:
                r = store._request(
                    method='POST',
                    url=url,
                    headers=kwargs['headers'],
                    body=data
                )
                
                # Always delete the temporary graph to clean up, even if POST failed
                delete_url = f"{store.gsp_endpoint}?graph={temp_graph_uri}"
                delete_r = store._request(
                    method='DELETE',
                    url=delete_url,
                    headers={}
                )
                
                if not delete_r.ok:
                    logger.warning(f"Warning: Failed to delete temporary graph {temp_graph_uri}: {delete_r.status_code}:\n{delete_r.text}")
                
                # Log error if POST failed
                if not r.ok:
                    logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")
            except Exception as e:
                logger.error(f"Error in publish: {e}")
        else:
            # Legacy behavior: POST without graph parameter
            try:
                r = store._request(
                    method='POST',
                    url=store.gsp_endpoint,
                    headers=kwargs['headers'],
                    body=data
                )
                if not r.ok:
                    logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")
            except Exception as e:
                logger.error(f"Error in publish: {e}")

    def put(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='turtle')
        
        kwargs = dict(
            headers={'Content-Type': 'text/turtle;charset=utf-8'},
        )
        
        if use_temp_graph:
            # Generate a temporary UUID-based graph URI
            temp_graph_uri = f"urn:uuid:{uuid.uuid4()}"
            
            # PUT to the temporary graph using authenticated request
            url = f"{store.gsp_endpoint}?graph={temp_graph_uri}"
            
            try:
                r = store._request(
                    method='PUT',
                    url=url,
                    headers=kwargs['headers'],
                    body=data.encode('utf-8') if isinstance(data, str) else data
                )
                
                # Always delete the temporary graph to clean up
                delete_url = f"{store.gsp_endpoint}?graph={temp_graph_uri}"
                delete_r = store._request(
                    method='DELETE',
                    url=delete_url,
                    headers={}
                )
                
                if not delete_r.ok:
                    logger.warning(f"Warning: Failed to delete temporary graph {temp_graph_uri}: {delete_r.status_code}:\n{delete_r.text}")
                
                # Log result
                if not r.ok:
                    logger.error(f"Error: {store.gsp_endpoint} PUT returned status {r.status_code}:\n{r.text}")
                else:
                    logger.debug(f"{r.text} {r.status_code}")
            except Exception as e:
                logger.error(f"Error in put: {e}")
        else:
            # Legacy behavior: PUT with specified graph identifier
            url = f"{store.gsp_endpoint}?graph={graph.identifier}"
            try:
                r = store._request(
                    method='PUT',
                    url=url,
                    headers=kwargs['headers'],
                    body=data.encode('utf-8') if isinstance(data, str) else data
                )
                if not r.ok:
                    logger.error(f"Error: {store.gsp_endpoint} PUT returned status {r.status_code}:\n{r.text}")
                else:
                    logger.debug(f"{r.text} {r.status_code}")
            except Exception as e:
                logger.error(f"Error in put: {e}")

    def post(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='trig')
        
        kwargs = dict(
            headers={'Content-Type': 'text/trig;charset=utf-8'},
        )
        
        if use_temp_graph:
            # Generate a temporary UUID-based graph URI
            temp_graph_uri = f"urn:uuid:{uuid.uuid4()}"
            
            # POST to the temporary graph using authenticated request
            url = f"{store.gsp_endpoint}?graph={temp_graph_uri}"
            
            try:
                r = store._request(
                    method='POST',
                    url=url,
                    headers=kwargs['headers'],
                    body=data.encode('utf-8') if isinstance(data, str) else data
                )
                
                # Always delete the temporary graph to clean up
                delete_url = f"{store.gsp_endpoint}?graph={temp_graph_uri}"
                delete_r = store._request(
                    method='DELETE',
                    url=delete_url,
                    headers={}
                )
                
                if not delete_r.ok:
                    logger.warning(f"Warning: Failed to delete temporary graph {temp_graph_uri}: {delete_r.status_code}:\n{delete_r.text}")
                
                # Log error if POST failed
                if not r.ok:
                    logger.error(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")
            except Exception as e:
                logger.error(f"Error in post: {e}")
        else:
            # Legacy behavior: POST without graph parameter
            try:
                r = store._request(
                    method='POST',
                    url=store.gsp_endpoint,
                    headers=kwargs['headers'],
                    body=data.encode('utf-8') if isinstance(data, str) else data
                )
                if not r.ok:
                    logger.error(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")
            except Exception as e:
                logger.error(f"Error in post: {e}")

    def delete(c):
        url = f"{store.gsp_endpoint}?graph={c}"
        try:
            r = store._request(
                method='DELETE',
                url=url,
                headers={}
            )
            if not r.ok:
                logger.error(f"Error: {store.gsp_endpoint} DELETE returned status {r.status_code}:\n{r.text}")
        except Exception as e:
            logger.error(f"Error in delete: {e}")

    store.publish = publish
    store.put = put
    store.post = post
    store.delete = delete
    
    return store


def _remote_sparql_store_protocol_with_aws(store, aws_auth, use_temp_graph=True):
    """
    Add Graph Store Protocol (GSP) operations with AWS authentication.
    
    DEPRECATED: This function is kept for backward compatibility with the old
    aws_requests_auth approach. New code should use NeptuneBoto3Store with
    _add_gsp_methods_to_boto3_store instead.
    
    This is similar to _remote_sparql_store_protocol but uses AWS SigV4 auth
    instead of basic auth.
    
    When use_temp_graph is True (default), publish/put/post operations use a
    temporary UUID-based graph URI to ensure graph-aware semantics. This prevents
    triples from being inserted into an explicit default graph and instead maintains
    the graph structure from the RDF data (e.g., TriG format).
    
    Args:
        store: A SPARQL store object with gsp_endpoint attribute
        aws_auth: AWSRequestsAuth object for request signing
        use_temp_graph: If True, use temporary UUID graphs for GSP operations (default: True)
        
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
        
        if use_temp_graph:
            # Generate a temporary UUID-based graph URI
            temp_graph_uri = f"urn:uuid:{uuid.uuid4()}"
            
            # POST to the temporary graph
            r = session.post(store.gsp_endpoint, 
                           params=dict(graph=temp_graph_uri),
                           data=data, 
                           **kwargs)
            
            # Always delete the temporary graph to clean up, even if POST failed
            delete_r = session.delete(store.gsp_endpoint,
                                    params=dict(graph=temp_graph_uri))
            if not delete_r.ok:
                logger.warning(f"Warning: Failed to delete temporary graph {temp_graph_uri}: {delete_r.status_code}:\n{delete_r.text}")
            
            # Log error if POST failed
            if not r.ok:
                logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")
        else:
            # Legacy behavior: POST without graph parameter
            r = session.post(store.gsp_endpoint, data=data, **kwargs)
            if not r.ok:
                logger.error(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")

    def put(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='turtle')
        
        kwargs = dict(
            headers={'Content-Type': 'text/turtle;charset=utf-8'},
        )
        
        if use_temp_graph:
            # Generate a temporary UUID-based graph URI
            temp_graph_uri = f"urn:uuid:{uuid.uuid4()}"
            
            # PUT to the temporary graph
            r = session.put(store.gsp_endpoint,
                          params=dict(graph=temp_graph_uri),
                          data=data,
                          **kwargs)
            
            # Always delete the temporary graph to clean up, even if PUT failed
            delete_r = session.delete(store.gsp_endpoint,
                                    params=dict(graph=temp_graph_uri))
            if not delete_r.ok:
                logger.warning(f"Warning: Failed to delete temporary graph {temp_graph_uri}: {delete_r.status_code}:\n{delete_r.text}")
            
            # Log result
            if not r.ok:
                logger.error(f"Error: {store.gsp_endpoint} PUT returned status {r.status_code}:\n{r.text}")
            else:
                logger.debug(f"{r.text} {r.status_code}")
        else:
            # Legacy behavior: PUT with specified graph identifier
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
        
        if use_temp_graph:
            # Generate a temporary UUID-based graph URI
            temp_graph_uri = f"urn:uuid:{uuid.uuid4()}"
            
            # POST to the temporary graph
            r = session.post(store.gsp_endpoint,
                           params=dict(graph=temp_graph_uri),
                           data=data,
                           **kwargs)
            
            # Always delete the temporary graph to clean up, even if POST failed
            delete_r = session.delete(store.gsp_endpoint,
                                    params=dict(graph=temp_graph_uri))
            if not delete_r.ok:
                logger.warning(f"Warning: Failed to delete temporary graph {temp_graph_uri}: {delete_r.status_code}:\n{delete_r.text}")
            
            # Log error if POST failed
            if not r.ok:
                logger.error(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")
        else:
            # Legacy behavior: POST without graph parameter
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
