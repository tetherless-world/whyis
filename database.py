# -*- coding:utf-8 -*-

import requests
import collections
from rdflib import Namespace, BNode, URIRef
from rdflib.graph import ConjunctiveGraph
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore, _node_to_sparql
from rdflib.plugins.stores.sparqlconnector import SPARQLConnectorException, _response_mime_types

import elasticstore

SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')

def node_to_sparql(node):
    if isinstance(node, BNode):
        return '<bnode:b%s>' % node
    return _node_to_sparql(node)

#def node_from_result(node):
#    if node.tag == '{%s}uri' % SPARQL_NS and node.text.startswith("bnode:"):
#        return BNode(node.text.replace("bnode:",""))
#    else:
#        return _node_from_result(node)

class WhyisSPARQLStore(SPARQLStore):
    
    def _inject_prefixes(self, query, extra_bindings):
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])

class WhyisSPARQLUpdateStore(SPARQLUpdateStore):

    # To resolve linter warning
    # "attribute defined outside  __init__"
    def __init__(self, *args, **kwargs):
        self.publish = None
        SPARQLUpdateStore.__init__(self, *args, **kwargs)

    def _inject_prefixes(self, query, extra_bindings):
        bindings = list(extra_bindings.items())
        if not bindings:
            return query
        return '\n'.join([
            '\n'.join(['PREFIX %s: <%s>' % (k, v) for k, v in bindings]),
            '',  # separate ns_bindings from query with an empty line
            query
        ])

    def _update(self, update):
        self._updates += 1
        
        if not self.update_endpoint:
            raise SPARQLConnectorException("Query endpoint not set!")

        params = {}

        headers = {
            'Accept': _response_mime_types[self.returnFormat],
            'Content-type': 'application/sparql-update'
        }

        args = dict(self.kwargs)

        args.update(url=self.update_endpoint,
                    data=update.encode('utf-8'))

        # merge params/headers dicts
        args.setdefault('params', {})
        args['params'].update(params)
        args.setdefault('headers', {})
        args['headers'].update(headers)

        res = self.session.post(**args)

        res.raise_for_status()
        
def create_query_store(store):
    new_store = WhyisSPARQLStore(endpoint=store.query_endpoint,
#                            method="POST",
#                            returnFormat='json',
                            node_to_sparql=node_to_sparql)
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
    if prefix+'elasticsearch' in config:
        store = elasticstore.ElasticSearchStore()
        store.open(config[prefix+'elasticsearch'], create=True)
        def publish(data, *graphs):
            for graph in graphs:
                store.addN(graph.quads(), graph.identifier.split('/')[-1])
        publish.serialize = True
        store.sparql = sparql_local

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

        publish.serialize = True
        graph.store.publish = publish

        
    return graph
