from flask import abort
from flask_security.datastore import Datastore
from rdflib import BNode, Literal, URIRef, Namespace, Graph, RDF, RDFS
from rdflib.graph import ConjunctiveGraph
from rdflib.resource import Resource

from .datastore_utils import *

class WhyisDatastore(Datastore):
    def __init__(self, db, classes, prefix):
        Datastore.__init__(self, db)
        db.datastore = self
        self.db = db
        self.classes = classes
        self.prefix = prefix

    def commit(self):
        pass
        #self.db.commit()

    def put(self, model):
        self.db.store.put(model.graph)
        return self.get(model.identifier, type(model))

    def delete(self, model):
        uri = model.graph.identifier
        idb = ConjunctiveGraph(self.db.store,uri)
        if not idb:
            abort(404, "Resource does not exist or is not deletable.")
        self.db.store.delete(uri)

    def get(self,resUri, c=None):
        idb = Graph(self.db.store,resUri)
        result = Graph(identifier=resUri)
        result += idb
        if c is None:
            c = Resource
            for t in result.objects(resUri, RDF.type):
                #print (resUri, t, t in self.classes)
                if t in self.classes:
                    c = self.classes[t]
        #print (c, resUri)
        res = c(result, resUri)
        res.datasource = self

        return res

    def find(self, model, **kwargs):
        rdf_type = model.rdf_type
        predicates = [(model.__dict__[key]._predicate, key) for key, value in kwargs.items()]
        bindings = { key: value2object(value) for key, value in kwargs.items() }
        query = ''' select ?identifier where {
        ?identifier a %s;
        ''' % rdf_type.n3() + '\n'.join(['    %s ?%s;' % (p.n3(), v) for p, v in predicates]) + '''
        .
        }'''
        result = list(self.db.query(query, initBindings=bindings))
        if result:
            return self.get(result[0][0], model)
        return None
