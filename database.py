# -*- coding:utf-8 -*-

import flask_ld as ld
from rdflib import *
SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore, _node_to_sparql, POST
from SPARQLWrapper import *

import requests

import collections

import elasticstore

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
    new_store = SPARQLStore(endpoint=store.endpoint,
                            default_query_method=POST,
                            returnFormat=JSON,
                            node_to_sparql=node_to_sparql)
    new_store._defaultReturnFormat=JSON
    new_store.setReturnFormat(JSON)
    return new_store

memory_graphs = collections.defaultdict(ConjunctiveGraph)


def sparql_remote(store, request):
    if request.method == 'GET':
        headers = {}
        headers.update(request.headers)
        if 'Content-Length' in headers:
            del headers['Content-Length']
        return requests.get(store.query_endpoint,
                            headers = headers, params=request.args)
    elif request.method == 'POST':
        if 'application/sparql-update' in request.headers['content-type']:
            return "Update not allowed.", 403
        return requests.post(store.query_endpoint, data=request.get_data(),
                            headers = request.headers, params=request.args)
            #print self.db.store.query_endpoint
            #print req.status_code


def sparql_local(store, request):

    q=request.values["query"]

    a=request.headers["Accept"]

    format="xml" # xml is default
    if mimeutils.JSON_MIME in a:
        format="json"
    if mimeutils.CSV_MIME in a:
        format="csv"
    if mimeutils.TSV_MIME in a:
        format="csv"

    # output parameter overrides header
    format=request.values.get("output", format)

    mimetype=mimeutils.resultformat_to_mime(format)

    # force-accept parameter overrides mimetype
    mimetype=request.values.get("force-accept", mimetype)

    return store.query(q).serialize(format=format)

def engine_from_config(config, prefix):
    defaultgraph = None
    if prefix+"defaultGraph" in config:
        defaultgraph = URIRef(config[prefix+"defaultGraph"])
    if prefix+"queryEndpoint" in config:
        store = SPARQLUpdateStore(queryEndpoint=config[prefix+"queryEndpoint"],
                                  update_endpoint=config[prefix+"updateEndpoint"],
                                  default_query_method=POST,
                                  returnFormat=JSON,
                                  node_to_sparql=node_to_sparql)
        def publish(data, *graphs):
            s = requests.session()
            s.keep_alive = False
            result = s.post(store.endpoint,
                            data=data,
#                            params={"context-uri":graph.identifier},
                            headers={'Content-Type':'application/x-trig'})

        store.publish = publish
        publish.serialize = False

        store._defaultReturnFormat=JSON
        store.setReturnFormat(JSON)
        store.sparql = sparql_remote
        graph = ConjunctiveGraph(store,defaultgraph)
    elif prefix+'store' in config:
        graph = ConjunctiveGraph(store='Sleepycat',identifier=defaultgraph)
        graph.store.batch_unification = False
        graph.store.open(config[prefix+"store"], create=True)
    elif prefix+'elasticsearch' in config:
        store = elasticstore.ElasticSearchStore()
        store.open(config[prefix+'elasticsearch'], create=True)
        def publish(data, *graphs):
            for graph in graphs:
                store.addN([(s,p,o,g) for s,p,o,g in graph.quads()], graph.identifier.split('/')[-1])
        publish.serialize = True
        store.sparql = sparql_local

        graph = ConjunctiveGraph(store=store)
        graph.store.publish = publish
    else:
        graph = memory_graphs[prefix]
        def publish(data, *graphs):
            for nanopub in graphs:
                graph.addN(nanopub.quads())
        publish.serialize = True
        graph.store.publish = publish

        
    return graph

