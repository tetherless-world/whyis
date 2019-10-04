from builtins import str
from builtins import range
from six import b
from six.moves.urllib.request import pathname2url
from six import iteritems

from rdflib.store import Store, VALID_STORE, NO_STORE
from rdflib.term import URIRef

import requests
from uuid import uuid4

import rdflib

import json

import logging
logger = logging.getLogger(__name__)

__all__ = ['ElasticSearchStore']
import pkg_resources

elastic_index_settings = pkg_resources.resource_string(__name__, "elastic_index_settings.json")

class ElasticSearchStore(Store):
    context_aware = True
    formula_aware = False
    transaction_aware = False
    graph_aware = True
    __prefix = {}
    __namespace = {}

    def __init__(self, configuration=None, identifier=None):
        self.__open = False
        self.__identifier = identifier
        super(ElasticSearchStore, self).__init__(configuration)

    def __get_identifier(self):
        return self.__identifier
    identifier = property(__get_identifier)

    def is_open(self):
        return self.__open

    def open(self, url, create=True):
        self.url = url
        self.session = requests.Session()
        status = self.session.get(url)
        if create and status.status_code == 404:
            r = self.session.put(self.url,data=elastic_index_settings,headers={"Content-Type":"application/json"})
            if r.status_code != 201:
                print(r.status_code)
                print(r.content)
        self.__open = True

        return VALID_STORE

    def sync(self):
        if self.__open:
            pass

    def close(self, commit_pending_transaction=False):
        if self.__open:
            #self.db_env.close()
            self.__open = False

    def add(self, triple, context, quoted=False, txn=None):
        """\
        Add a triple to the store of triples.
        """
        (subject, predicate, object) = triple
        assert self.__open, "The Store must be open."
        assert context != self, "Can not add triple directly to store"
        self.addN([(subject,predicate,object,context)])

    def addN(self, quads, docid = None):
        """
        Adds each item in the list of statements to a specific context. The
        quoted argument is interpreted by formula-aware stores to indicate this
        statement is quoted/hypothetical.
        """
        assert self.__open, "The Store must be open."

        graphs = {}
        resources = {}
        json_ld = []
        bnodes = {}
        def skolemize_bnodes(x):
            if isinstance(x, rdflib.Graph):
                x = x.identifier
            if isinstance(x, rdflib.BNode):
                if x not in bnodes:
                    bnodes[x] = '_:'+uuid4().hex
                return bnodes[x]
            else:
                return x
            
        for quad in quads:
            s, p, o, g = [skolemize_bnodes(x) for x in quad]
            if g not in graphs:
                graphs[g] = {"@id":str(g),"@graph":[]}
                json_ld.append(graphs[g])
            if (g,s) not in resources:
                resources[(g,s)] = {"@id":str(s), "@object" : []}
                graphs[g]['@graph'].append(resources[(g,s)])
            resource = resources[(g,s)]
            if p not in resource:
                resource[str(p)] = []
            if isinstance(o, rdflib.Literal):
                obj = {"@value" : str(o)}
                if o.datatype is not None:
                    obj['@type'] = str(o.datatype)
                if o.language is not None:
                    obj['@lang'] = str(o.language)
            else:
                obj = {"@id" : str(o)}
            resource[str(p)].append(obj)
            resource['@object'].append(obj)

        json_ld = json.dumps({ "graphs": json_ld })

        if docid is None:
            docid = uuid4().hex
        r = self.session.put(self.url+'/nanopublication/'+docid,
                             headers={"Content-Type":"application/json"},
                             data=json_ld)
        if r.status_code != 201:
            print(r.status_code)
            print(r.content)
    
    def remove(self, spo, context, txn=None):
        subject, predicate, object = spo
        assert False, "remove() is not implemented."

    def elastic_query(self, query):
        query = {
            "query": {
                "nested" : {
                    "path" : "graphs.@graph",
                    "score_mode" : "avg",
                    "query" : query
                }
            }
        }
        response = self.session.post(self.url+"/_search",data=json.dumps(query),
                                     headers={"Content-Type":"application/json"})

        return response.json()
        
    def triples(self, spo, context=None, txn=None):
        """A generator over all the triples matching """
        assert self.__open, "The Store must be open."

        subject, predicate, object = spo

        if context is not None:
            if context == self:
                context = None
            else:
                context = context.identifier

        query = {
            "query": {
                "nested" : {
                    "path" : "graphs.@graph",
                    "score_mode" : "avg",
                    "query" : {
                        "bool" : {
                            "must" : [
                            ]
                        }
                    }
                }
            }
        }
        match_all = True
        if subject is not None:
            match_all = False
            query['query']['nested']['query']['bool']['must'].append( { "term" : { "graphs.@graph.@id" : str(subject) } } )
        if predicate is not None and object is None:
            match_all = False
            query['query']['nested']['query']['bool']['must'].append( { "exists" : { 'field': "graphs.@graph."+str(predicate) } } )
        if object is not None:
            match_all = False
            obj_path = ''
            if isinstance(object, rdflib.Literal):
                obj_path = obj_path + '.@value'
            else:
                obj_path = obj_path + '.@id'
            if predicate is not None:
                query['query']['nested']['query']['bool']['must'].append( { "term" : {
                      "graphs.@graph."+str(predicate) +obj_path : str(object)
                    } } )
            else:
                query['query']['nested']['query']['bool']['must'].append( { "term" : {
                     "graphs.@graph.@object" +obj_path : str(object)
                    } } )
        if context is not None:
            match_all = False
            query['query']['nested']['query']['bool']['must'].append( { "exists" : {
                 'field': "graphs.@id."+str(context.identifier)
                } } )

        if match_all:
            query['query']['nested']['query'] = {'match_all': {}}

        response = self.session.post(self.url+"/_search",data=json.dumps(query),
                                     headers={"Content-Type":"application/json"})

        json_response = response.json()
        
        for hit in json_response['hits']['hits']:
            for graph in hit['_source']['graphs']:
                graphid = rdflib.URIRef(graph['@id'])
                if context is not None and context.identifier != graphid:
                    continue
                for resource in graph['@graph']:
                    resourceid = rdflib.URIRef(resource['@id'])
                    if subject is not None and subject != resourceid:
                        continue
                    predicates = []
                    if predicate is not None:
                        predicates = [str(predicate)]
                    else:
                        predicates = list(resource.keys())
                    for pred in predicates:
                        if pred == '@object' or pred == '@id':
                            continue
                        if pred not in resource:
                            continue
                        for obj in resource[pred]:
                            o = None
                            if '@id' in obj:
                                id = obj['@id']
                                if id.startswith('_:'):
                                    o = rdflib.BNode(id[2:])
                                else:
                                    o = rdflib.URIRef(id)
                            else:
                                args = {}
                                if '@type' in obj:
                                    args['datatype'] = rdflib.URIRef(obj['@type'])
                                if '@lang' in obj:
                                    args['lang'] = obj['@lang']
                                o = rdflib.Literal(obj['@value'],**args)
                            if object is not None and o != object:
                                continue
                            yield (resourceid, rdflib.URIRef(pred), o), graphid

    def __len__(self, context=None):
        assert self.__open, "The Store must be open."
        assert False, "Not implemented."
        return 0

    def bind(self, prefix, namespace):
        self.__prefix[namespace] = prefix
        self.__namespace[prefix] = namespace

    def namespace(self, prefix):
        return self.__namespace.get(prefix, None)

    def prefix(self, namespace):
        return self.__prefix.get(namespace, None)

    def namespaces(self):
        for prefix, namespace in iteritems(self.__namespace):
            yield prefix, namespace

    def contexts(self, triple=None):
        assert False, "Not implemented."
        for i in range(0):
            yield(URIRef())

    def add_graph(self, graph):
        json_ld = graph.serialize(format='json-ld')
        docid = uuid4().hex
        self.session.put(self.url+'/nanopublication/'+docid, data=json_ld)

    def remove_graph(self, graph):
        self.remove((None, None, None), graph)
