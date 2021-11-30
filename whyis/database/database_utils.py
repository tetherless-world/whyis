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

def engine_from_config(config, prefix):
    defaultgraph = None
    if "DEFAULT_GRAPH" in config:
        defaultgraph = URIRef(config["_default_graph"])
    if "_endpoint" in config:
        store = WhyisSPARQLUpdateStore(query_endpoint=config["_endpoint"],
                                  update_endpoint=config["_endpoint"],
                                  method="POST",
                                  returnFormat='json',
                                  node_to_sparql=node_to_sparql)
        store.query_endpoint = config[prefix+"queryEndpoint"]
        def publish(data, format='application/x-trig;charset=utf-8'):
            s = requests.session()
            s.keep_alive = False

            if config.get("USE_BLAZEGRAPH_BULK_LOAD",False):
                # TODO: we aren't using blazegraph anymore,
                # but should we keep supportin this?
                prop_file = '''
quiet=false
verbose=1
closure=false
durableQueues=true
#Needed for quads
defaultGraph=%s
format=text/x-nquads
com.bigdata.rdf.store.DataLoader.flush=false
com.bigdata.rdf.store.DataLoader.bufferCapacity=100000
com.bigdata.rdf.store.DataLoader.queueCapacity=10
#Namespace to load
namespace=%s
propertyFile=%s
#Files to load
fileOrDirs=%s''' % (config['LOD_PREFIX']+'/pub/'+create_id()+"_assertion",
                    config["BULK_LOAD_NAMESPACE"],
                    config["BLAZEGRAPH_PROPERTIES"],
                    data.name)
                r = s.post(config["BULK_LOAD_ENDPOINT"],
                           data=prop_file.encode('utf8'),
                           headers={'Content-Type':'text/plain'})


            else:
                # result unused
                r = s.post(store.query_endpoint,
                           data=data,
                           # params={"context-uri":graph.identifier},
                           headers={'Content-Type':format})
                #print(r.text)

        store.publish = publish

        graph = ConjunctiveGraph(store,defaultgraph)
    elif '_store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config["STORE"], create=True)
    else:
<<<<<<< HEAD
        graph = ConjunctiveGraph()

        def publish(data):
            graph.parse(data, format='nquads')

        graph.store.publish = publish

=======
        graph = ConjunctiveGraph() # memory_graphs[prefix]

        def publish(data):
            graph.parse(data, format='trig')

        graph.store.publish = publish


>>>>>>> master
    return graph
