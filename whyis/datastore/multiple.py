from copy import copy
from rdflib import BNode, Literal, URIRef, RDF

from .datastore_utils import *


class multiple:
    '''This is a Descriptor
       Expects to return a list of values (could be a list of one)'''
    def __init__(self, predicate):
        self._predicate = predicate

    def __get__(self, obj, cls):
        if obj is None:
            return self
        #if self._predicate in obj.__dict__:
        #    return obj.__dict__[self._predicate]
        val = list(obj.graph.objects(obj.identifier, self._predicate))
        # check to see if this is a Container or Collection
        # if so, return collection as a list
        if len(val) == 1 and not isinstance(val[0], Literal) and obj.graph.value(val[0], RDF.first):
            val = getList(obj, self._predicate)
            
        # print(val)
        val = [(obj.datastore.get(v) if isinstance(v, (BNode, URIRef))
                else v.toPython())
               for v in val]
        #obj.__dict__[self.name] = val
        #print (val)
        return val

    def __set__(self, obj, newvals):
        if not isinstance(newvals, (list, tuple)):
            raise AttributeError("to set a rdfMultiple you must pass in "
                                 + "a list (it can be a list of one)" )
        try:
            oldvals = obj.__dict__[self._predicate]
        except KeyError:
            oldvals = []
            obj.__dict__[self._predicate] = oldvals
        db = obj.graph
        for value in oldvals:
            if value and value not in newvals:
                db.remove((obj.identifier, self._predicate, value2object(value)))
        for value in newvals:
            if value not in oldvals:
                db.add((obj.identifier, self._predicate, value2object(value)))
        obj.__dict__[self._predicate] = copy(newvals)

