# -*- coding:utf-8 -*-

import flask_ld as ld
from rdflib import *
SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')
from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore, _node_to_sparql, _node_from_result

def node_to_sparql(node):
    if isinstance(node, BNode):
        return '<bnode:b%s>' % node
    return _node_to_sparql(node)

def node_from_result(node):
    if node.tag == '{%s}uri' % SPARQL_NS and node.text.startswith("bnode:"):
        return BNode(node.text.replace("bnode:",""))
    else:
        return _node_from_result(node)
    
def engine_from_config(config, prefix):
    defaultgraph = None
    if prefix+"defaultGraph" in config:
        defaultgraph = URIRef(config[prefix+"defaultGraph"])
    if prefix+"queryEndpoint" in config:
        store = SPARQLUpdateStore(queryEndpoint=config[prefix+"queryEndpoint"],
                                  update_endpoint=config[prefix+"updateEndpoint"],
                                  default_query_method="POST",
                                  node_to_sparql=node_to_sparql,
                                  node_from_result=node_from_result)
        graph = ConjunctiveGraph(store,defaultgraph)
    elif prefix+'store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config[prefix+"store"], create=True)
    else:
        graph = ConjunctiveGraph(identifier=defaultgraph)
    return graph

