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

from .single import single
from .multiple import multiple
from .mapped_resource import MappedResource

class User(MappedResource, UserMixin):
    rdf_type = prov.Agent

    key = 'id'

    id = single(dc.identifier)
    active = single(auth.active)
    confirmed_at = single(auth.confirmed)
    email = single(auth.email)
    current_login_at = single(auth.hadCurrentLogin)
    current_login_ip = single( auth.hadCurrentLoginIP)
    last_login_at = single( auth.hadLastLogin)
    last_login_ip = single( auth.hadLastLoginIP)
    login_count = single( auth.hadLoginCount)
    roles = multiple( auth.hasRole)
    password = single( auth.passwd)
    familyName = single(foaf.familyName)
    givenName = single(foaf.givenName)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def verify_and_update_password(self, password):
        return verify_and_update_password(password, self)
