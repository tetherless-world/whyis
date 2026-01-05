# -*- coding:utf-8 -*-

import requests
from requests.auth import HTTPBasicAuth
from rdflib import BNode, URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.plugins.stores.sparqlstore import _node_to_sparql

from uuid import uuid4
from whyis.datastore import create_id

# SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')


from .whyis_sparql_store import WhyisSPARQLStore
from .whyis_sparql_update_store import WhyisSPARQLUpdateStore

def node_to_sparql(node):
    if isinstance(node, BNode):
        return '<bnode:b%s>' % node
    return _node_to_sparql(node)

#def node_from_result(node):
#    if node.tag == '{%s}uri' % SPARQL_NS and node.text.startswith("bnode:"):
#        return BNode(node.text.replace("bnode:",""))
#    else:
#        return _node_from_result(node)

drivers = {}

def driver(name):
    def inner(fn):
        #print("registering", fn, name)
        drivers[name] = fn
        return fn
    return inner

def _local_sparql_store_protocol(store):
    def publish(data):
        store.parse(data, format='trig')

    def put(graph):
        idb = Graph(store,graph.identifier)
        if idb:
            idb.remove((None,None,None))
        idb += model.graph

    def post(graph):
        idb = Graph(store,graph.identifier)
        idb += graph

    def delete(c):
        store.remove((None, None, None), c)
        
    store.publish = publish
    store.put = put
    store.delete = delete
    store.post = post
    return store

@driver(name="memory")
def memory_driver(config):
    graph = ConjunctiveGraph()

    store = _local_sparql_store_protocol(graph.store)
    return graph

@driver(name="oxigraph")
def oxigraph_driver(config):
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    graph = ConjunctiveGraph(store='Oxigraph',identifier=defaultgraph)
    graph.store.batch_unification = False
    graph.store.open(config["_store"], create=True)

    store = _local_sparql_store_protocol(graph.store)

    return graph

def _remote_sparql_store_protocol(store):
    """
    Add Graph Store Protocol (GSP) operations to a SPARQL store.
    
    This function adds publish, put, post, and delete methods to the store
    that use the store.gsp_endpoint for all HTTP operations. The gsp_endpoint
    should be configured separately from query_endpoint to allow different
    endpoints for SPARQL queries vs. graph manipulation.
    
    Args:
        store: A SPARQL store object with gsp_endpoint and auth attributes
        
    Returns:
        The store object with GSP methods attached
    """
    def publish(data, format='application/trig'):
        s = requests.session()
        s.keep_alive = False

        kwargs = dict(
            headers={'Content-Type':format},
        )
        if store.auth is not None:
            kwargs['auth'] = store.auth
        r = s.post(store.gsp_endpoint,
                   params=dict(default='true'),
                   data=data,
                   **kwargs)
        if not r.ok:
            print(f"Error: {store.gsp_endpoint} publish returned status {r.status_code}:\n{r.text}")

    def put(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='turtle')
        #print(data)
        s = requests.session()
        s.keep_alive = False

        kwargs = dict(
            headers={'Content-Type':'text/turtle'},
        )
        if store.auth is not None:
            kwargs['auth'] = store.auth
        r = s.put(store.gsp_endpoint,
                  params=dict(graph=graph.identifier),
                  data=data,
                  **kwargs)
        if not r.ok:
            print(f"Error: {store.gsp_endpoint} PUT returned status {r.status_code}:\n{r.text}")
        else:
            print(r.text, r.status_code)

    def post(graph):
        g = ConjunctiveGraph(store=graph.store)
        data = g.serialize(format='trig')
        s = requests.session()
        s.keep_alive = False

        kwargs = dict(
            headers={'Content-Type':'application/trig'},
        )
        if store.auth is not None:
            kwargs['auth'] = store.auth
        r = s.post(store.gsp_endpoint, params=dict(default="true"), data=data, **kwargs)
        if not r.ok:
            print(f"Error: {store.gsp_endpoint} POST returned status {r.status_code}:\n{r.text}")

    def delete(c):
        s = requests.session()
        s.keep_alive = False

        kwargs = dict(
        )
        if store.auth is not None:
            kwargs['auth'] = store.auth
        r = s.delete(store.gsp_endpoint,
                     params=dict(graph=c),
                     **kwargs)
        if not r.ok:
            print(f"Error: {store.gsp_endpoint} DELETE returned status {r.status_code}:\n{r.text}")
        
    store.publish = publish
    store.put = put
    store.delete = delete
    store.post = post
    return store

@driver(name="sparql")
def sparql_driver(config):
    """
    Create a SPARQL-based RDF graph store.
    
    Configuration options (via Flask config with prefix like KNOWLEDGE_ or ADMIN_):
    - _endpoint: SPARQL query/update endpoint (required)
    - _gsp_endpoint: Graph Store Protocol endpoint (optional, defaults to _endpoint)
    - _username: Authentication username (optional)
    - _password: Authentication password (optional)
    - _default_graph: Default graph URI (optional)
    
    Example configuration in system.conf:
        KNOWLEDGE_ENDPOINT = 'http://localhost:3030/knowledge/sparql'
        KNOWLEDGE_GSP_ENDPOINT = 'http://localhost:3030/knowledge/data'  # optional
    
    If _gsp_endpoint is not provided, all Graph Store Protocol operations
    (publish, put, post, delete) will use the _endpoint value, maintaining
    backward compatibility with existing configurations.
    """
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    kwargs = dict(
        query_endpoint=config["_endpoint"],
        update_endpoint=config["_endpoint"],
        method="POST",
        returnFormat='json',
        node_to_sparql=node_to_sparql
    )
    if '_username' in config:
        kwargs['auth'] = (config['_username'], config['_password'])
    store = WhyisSPARQLUpdateStore(**kwargs)
    store.query_endpoint = config["_endpoint"]
    # Set GSP endpoint: use _gsp_endpoint if provided, otherwise fall back to query_endpoint
    store.gsp_endpoint = config.get("_gsp_endpoint", config["_endpoint"])
    if 'auth' in kwargs:
        store.auth = kwargs['auth']
    else:
        store.auth = None

    store = _remote_sparql_store_protocol(store)
    
    graph = ConjunctiveGraph(store,defaultgraph)
    return graph

def create_query_store(store):
    """
    Create a read-only query store from an existing store.
    
    This function creates a query-only store that can be used for read operations
    without update capabilities.
    
    Args:
        store: The source store object
        
    Returns:
        A new store configured for queries only
    """
    new_store = WhyisSPARQLStore(
        endpoint=store.query_endpoint,
        query_endpoint=store.query_endpoint,
        node_to_sparql=node_to_sparql
    )
    return new_store

# memory_graphs = collections.defaultdict(ConjunctiveGraph)

def engine_from_config(config):
    engine = None
    if "_endpoint" in config:
        engine = drivers['sparql'](config)
    elif '_store' in config:
        engine = drivers['oxigraph'](config)
    elif '_memory' in config:
        engine = drivers['memory'](config)
    else:
        t = config['_type']
        engine = drivers[t](config)
    return engine
