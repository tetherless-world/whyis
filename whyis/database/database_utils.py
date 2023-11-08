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
    def decorator(function):
        drivers[name] = function
        return function
    return decorator

def driver(name):
    def inner(fn):
        print("registering", fn, name)
        drivers[name] = fn
        return fn
    return inner

@driver(name="memory")
def memory_driver(config):
    graph = ConjunctiveGraph()

    def publish(data):
        graph.parse(data, format='trig')

    graph.store.publish = publish

    return graph

@driver(name="oxigraph")
def oxigraph_driver(config):
    defaultgraph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    graph = ConjunctiveGraph(store='Oxigraph',identifier=defaultgraph)
    graph.store.batch_unification = False
    graph.store.open(config["_store"], create=True)

    def publish(data):
        graph.parse(data, format='trig')

    graph.store.publish = publish

    return graph

@driver(name="sparql")
def sparql_driver(config):
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
    if 'auth' in kwargs:
        store.auth = kwargs['auth']
    else:
        store.auth = None

    def publish(data, format='text/trig;charset=utf-8'):
        s = requests.session()
        s.keep_alive = False

        kwargs = dict(
            headers={'Content-Type':format},
        )
        if store.auth is not None:
            kwargs['auth'] = store.auth
        r = s.post(store.query_endpoint, data=data, **kwargs)
        #print(r.text)
    store.publish = publish

    graph = ConjunctiveGraph(store,defaultgraph)
    return graph

def create_query_store(store):
    new_store = WhyisSPARQLStore(endpoint=store.query_endpoint,
                                 query_endpoint=store.query_endpoint,
#                            method="POST",
#                            returnFormat='json',
                            node_to_sparql=node_to_sparql)
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
