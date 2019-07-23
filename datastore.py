from copy import copy
from flask import abort
from flask_security import UserMixin, RoleMixin
from flask_security.utils import verify_and_update_password
from flask_security.datastore import Datastore, UserDatastore
from namespace import dc, auth, foaf, prov
from rdflib import BNode, Literal, URIRef, Namespace, Graph, RDF, RDFS
from rdflib.graph import ConjunctiveGraph
from rdflib.resource import Resource
from rdflib.term import Identifier

import base64
import random
from datetime import datetime


def create_id():
    return base64.encodestring(str(random.random() * datetime.now().toordinal()).encode('utf8')).decode('utf8').rstrip(
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

class MappedResource(Resource):

    rdf_type = None
    key = None

    def __init__(self, graph=None, subject=None, **kwargs):

        if subject is None and self.key in kwargs:
            subject = self.prefix[kwargs[self.key]]

        if graph is None:
            graph = ConjunctiveGraph(identifier=subject)
            
        Resource.__init__(self,graph, subject)

        if self.rdf_type and not self[RDF.type:self.rdf_type]:
            self.graph.add((self.identifier, RDF.type, self.rdf_type))
            
        if kwargs:
            self._set_with_dict(kwargs)

    def _set_with_dict(self, kv):
        """
        :param kv: a dict

          for each key,value pair in dict kv
               set self.key = value

        """
        for key, value in list(kv.items()):
            descriptor = self.__class__._getdescriptor(key)
            descriptor.__set__(self, value)
            
    @classmethod
    def _getdescriptor(cls, key):
        """__get_descriptor returns the descriptor for the key.
        It essentially cls.__dict__[key] with recursive calls to super"""
        # NOT SURE if mro is the way to do this or if we should call super or bases?
        for kls in cls.mro():
            if key in kls.__dict__:
                return kls.__dict__[key]
        raise AttributeError("descriptor %s not found for class %s" % (key,cls))

#    def __str__(self):
#        return type(self).__name__ + ' ' + super().__str__() + ' a ' + self.rdf_type

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


###  http://www.w3.org/ns/prov#Role

class Role(MappedResource, RoleMixin):
    rdf_type = prov.Role
    name = single(RDFS.label)
    key = 'name'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class WhyisDatastore(Datastore):

    def __init__(self, db, classes, prefix):
        Datastore.__init__(self, db)
        db.datastore = self
        self.db = db
        self.classes = classes
        self.prefix = prefix

    def commit(self):
        self.db.commit()

    def put(self, model):
        #self.db.add(model)
        idb = Graph(self.db.store,model.identifier)
        if idb:
            idb.remove((None,None,None))
        idb += model.graph
        self.db.store.commit()
        
        return self.get(model.identifier, type(model))

    def delete(self, model):
        uri = model.identifier
        idb = ConjunctiveGraph(self.db.store,uri)
        if not idb:
            abort(404, "Resource does not exist or is not deletable.")
        idb.remove((None,None,None))
        g = ConjunctiveGraph(self.db.store)
        g.remove((uri,None,None))
        g.remove((None,None,uri))
        self.delete(model.identifier)

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
        bindings = dict([(key, value2object(value)) for key, value in kwargs.items()])
        query = ''' select ?identifier where {
        ?identifier a %s;
        ''' % rdf_type.n3() + '\n'.join(['    %s ?%s;' % (p.n3(), v) for p, v in predicates]) + '''
        .
        }'''
        result = list(self.db.query(query, initBindings=bindings))
        if result:
            return self.get(result[0][0], model)


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
