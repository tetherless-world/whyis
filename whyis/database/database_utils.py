# -*- coding:utf-8 -*-

import requests
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


def create_query_store(store):
    new_store = WhyisSPARQLStore(endpoint=store.query_endpoint,
                                 query_endpoint=store.query_endpoint,
#                            method="POST",
#                            returnFormat='json',
                            node_to_sparql=node_to_sparql)
    return new_store

# memory_graphs = collections.defaultdict(ConjunctiveGraph)

def engine_from_config(config):
    defaultgraph = None
    graph = None
    if "_default_graph" in config:
        defaultgraph = URIRef(config["_default_graph"])
    if "_endpoint" in config:
        store = WhyisSPARQLUpdateStore(query_endpoint=config["_endpoint"],
                                  update_endpoint=config["_endpoint"],
                                  method="POST",
                                  returnFormat='json',
                                  node_to_sparql=node_to_sparql)
        store.query_endpoint = config["_endpoint"]
        def publish(data, format='text/trig;charset=utf-8'):
            s = requests.session()
            s.keep_alive = False

            r = s.post(store.query_endpoint,
                       data=data,
                       #params={"graph":default_graph},
                       headers={'Content-Type':format})
            #print(r.text)
        store.publish = publish

        graph = ConjunctiveGraph(store,defaultgraph)
    elif '_store' in config:
        graph = ConjunctiveGraph(store='Oxigraph',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config["_store"], create=True)
    elif '_memory' in config:
        try:
            raise Exception()
        except Exception as e:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)

        graph = ConjunctiveGraph()

        def publish(data):
            graph.parse(data, format='trig')

        graph.store.publish = publish

    return graph
