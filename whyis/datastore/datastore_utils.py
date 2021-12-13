from rdflib import BNode, Literal, URIRef, RDF
from rdflib.resource import Resource
from rdflib.term import Identifier

import base64
import random
from datetime import datetime

__all__ = ["create_id", "value2object", "tag_datastore", "getList"]

def create_id():
    return base64.encodebytes(str(random.random() * datetime.now().toordinal()).encode('utf8')).decode('utf').rstrip(
        '=\n')

def value2object(value):
    """
    Suitable for a triple takes a value and returns a Literal, URIRef or BNode
    suitable for a triple"""
    if isinstance(value, Resource):
        return value.identifier

    if isinstance(value, (Identifier, BNode, URIRef)):
        return value

    return Literal(value)

def tag_datastore(fn):
    def f(self,*args,**kw):
        result = fn(self,*args,**kw)
        if result:
            #print self, result
            result.datastore = self
        return result
    return f

# helper function, might be somewhere in rdflib I need to look for it there
def getList(sub, pred=None, db=None):
    """Attempts to return a list from sub (subject that is)
    passed in if it is a Collection or a Container (Bag,Seq or Alt)"""
    if not db:
        db = sub.graph
    if isinstance(sub, Resource):
        sub = sub.identifier
    if pred:
        base = db.value(sub, pred, any=True)
    else:
        # if there was no predicate assume a base node was passed in
        base = sub
    if not isinstance(base, BNode):
        # Doesn't look like a list or a collection, just return
        # multiple values (or an error?)
        val = [o for o in db.objects(sub, pred)]
        return val
    members = []
    first = db.value(base, RDF.first)
    # OK let's work at returning a list if there is an RDF.first
    if first:
        while first:
            members.append(first)
            base = db.value(base, RDF.rest)
            first = db.value(base, RDF.first)
        return members
    # OK let's work at returning a Collection (Seq,Bag or Alt)
    # if was no RDF.first

    i = 1
    # first = db.value(base, RDF._1) # _1 ???
    first = db.value(base, RDF.first)
    if not first:
        raise AttributeError(
            "Not a list, or collection but another type of BNode")
    while first:
        members.append(first)
        i += 1
        first = db.value(base, RDF['_%d' % i])
    return members
