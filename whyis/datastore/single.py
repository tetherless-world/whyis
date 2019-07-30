from copy import copy
from flask import abort
from flask_security import UserMixin, RoleMixin
from flask_security.utils import verify_and_update_password
from flask_security.datastore import Datastore, UserDatastore
from whyis.namespace import dc, auth, foaf, prov
from rdflib import BNode, Literal, URIRef, Namespace, Graph, RDF, RDFS
from rdflib.graph import ConjunctiveGraph
from rdflib.resource import Resource
from rdflib.term import Identifier

import base64
import random
from datetime import datetime

from .datastore_utils import *

class single:
    def __init__(self, predicate):
        self._predicate = predicate

    def __get__(self, obj, cls):
        if obj is None:
            return self
        if self._predicate in obj.__dict__:
            return obj.__dict__[self._predicate]
        val = obj.graph.value(obj.identifier, self._predicate)
        if isinstance(val, Literal):
            val = val.toPython()
        elif isinstance(val, (BNode, URIRef)):
            val = obj.datastore.get(val)
        obj.__dict__[self._predicate] = val
        return val

    def __set__(self, obj, value):
        obj.__dict__[self._predicate] = value
        o = value2object(value)
        obj.graph.set((obj.identifier, self._predicate, o))
