# -*- coding:utf-8 -*-

from flask.ext import ld
from rdflib import *

def engine_from_config(config, prefix):
    defaultgraph = None
    if prefix+"defaultGraph" in config:
        defaultgraph = URIRef(config[prefix+"defaultGraph"])
    if prefix+"queryEndpoint" in config:
        from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
        store = SPARQLUpdateStore(queryEndpoint=config[prefix+"queryEndpoint"],
                                  update_endpoint=config[prefix+"updateEndpoint"])
        graph = ConjunctiveGraph(store,defaultgraph)
    elif prefix+'store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config[prefix+"store"], create=True)
    else:
        graph = ConjunctiveGraph(identifier=defaultgraph)
    return graph

