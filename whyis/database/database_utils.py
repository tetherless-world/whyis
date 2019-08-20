# -*- coding:utf-8 -*-

import requests
from rdflib import BNode, URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.plugins.stores.sparqlstore import _node_to_sparql

# SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')


from .whyis_sparql_store import WhyisSPARQLStore
from .whyis_sparql_update_store import WhyisSPARQLUpdateStore
from .elasticstore import ElasticSearchStore

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
#                            method="POST",
#                            returnFormat='json',
                            node_to_sparql=node_to_sparql)
    return new_store

# memory_graphs = collections.defaultdict(ConjunctiveGraph)
        
def engine_from_config(config, prefix):
    defaultgraph = None
    if prefix+"defaultGraph" in config:
        defaultgraph = URIRef(config[prefix+"defaultGraph"])
    if prefix+'elasticsearch' in config:
        store = elasticstore.ElasticSearchStore()
        store.open(config[prefix+'elasticsearch'], config[prefix+'elasticIndex'], create=True)

        def publish(data, *graphs):
            for graph in graphs:
                store.addN(graph.quads(), graph.identifier.split('/')[-1])
        publish.serialize = True
        #store.sparql = sparql_local TODO restore this

        graph = ConjunctiveGraph(store=store)
        graph.store.publish = publish
    elif prefix+"queryEndpoint" in config:
        store = WhyisSPARQLUpdateStore(queryEndpoint=config[prefix+"queryEndpoint"],
                                  update_endpoint=config[prefix+"updateEndpoint"],
                                  method="POST",
                                  returnFormat='json',
                                  node_to_sparql=node_to_sparql)
        
        def publish(data, *graphs):
            s = requests.session()
            s.keep_alive = False
            
            # result unused
            s.post(store.query_endpoint,
                   data=data,
                   # params={"context-uri":graph.identifier},
                   headers={'Content-Type':'application/x-trig'})

        store.publish = publish

        graph = ConjunctiveGraph(store,defaultgraph)
    elif prefix+'store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config[prefix+"store"], create=True)
    else:
        graph = ConjunctiveGraph() # memory_graphs[prefix]
        
        def publish(data, *graphs):
            for nanopub in graphs:
                graph.addN(nanopub.quads())
                
        graph.store.publish = publish

        
    return graph
