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
from .whyis_datastore import WhyisDatastore
from .user import User
from .role import Role


class WhyisUserDatastore(WhyisDatastore, UserDatastore):
    def __init__(self, db, classes, prefix):
        classes[User.rdf_type] = User
        classes[Role.rdf_type] = Role
        self.User = User
        self.Role = Role
        self.User.prefix = Namespace(prefix+'/user/')
        self.Role.prefix = Namespace(prefix+'/role/')
        WhyisDatastore.__init__(self, db, classes, prefix)
        UserDatastore.__init__(self, User, Role)

    @tag_datastore
    def get_user(self, identifier):
        if isinstance(identifier, URIRef):
            return self.get(identifier, self.User)
        for attr in [dc.identifier, auth.email]:
            uri = self.db.value(predicate=attr, object=Literal(identifier))
            if uri is not None:
                return self.get(uri, self.User)
        return None

    @tag_datastore
    def find_user(self, **kwargs):
        if 'identifier' in kwargs:
            return self.get(URIRef(kwargs['identifier']))
        return self.find(User, **kwargs)

    @tag_datastore
    def find_role(self, role_name, **kwargs):
        role_uri = self.Role.prefix[role_name]
        if (role_uri, RDF.type, self.Role.rdf_type) not in self.db:
            self.put(self.Role(name=role_name))
        role = self.get(self.Role.prefix[role_name], self.Role)
        return role
