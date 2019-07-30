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

from .single import single
from .mapped_resource import MappedResource

###  http://www.w3.org/ns/prov#Role
class Role(MappedResource, RoleMixin):
    rdf_type = prov.Role
    name = single(RDFS.label)
    key = 'name'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
