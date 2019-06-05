from flask_security.datastore import Datastore, UserDatastore
from rdflib import *
from rdflib.resource import Resource
from rdflib.term import Identifier
from flask import make_response
from copy import copy
from flask_security import Security, \
    UserMixin, RoleMixin, login_required

from utils import create_id

def value2object(value):
    """
    Suitable for a triple takes a value and returns a Literal, URIRef or BNode
    suitable for a triple"""
    if isinstance(value, Resource):
        return value.identifier
    elif isinstance(value, Identifier) or isinstance(value, BNode) or isinstance(value, URIRef):
        return value
    else:
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
    else:
        i = 1
        first = db.value(base, RDF._1)
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
        val = [o for o in obj.graph.objects(obj.identifier, self._predicate)]
        # check to see if this is a Container or Collection
        # if so, return collection as a list
        if (len(val) == 1
            ) and (
                not isinstance(val[0], Literal)
            ) and (
                obj.graph.value(val[0], RDF.first
                             ) ):
            val = getList(obj, self._predicate)
        val = [(obj.datastore.get(v) if isinstance(v, (BNode, URIRef))
                else v.toPython())
               for v in val]
        #obj.__dict__[self.name] = val
        return val

    def __set__(self, obj, newvals):
        if not isinstance(newvals, (list, tuple)):
            raise AttributeError(
                "to set a rdfMultiple you must pass in " +
                "a list (it can be a list of one)")
        try:
            oldvals = obj.__dict__[self._predicate]
        except KeyError:
            oldvals = []
            obj.__dict__[self._predicate] = oldvals
        db = obj.graph
        for value in oldvals:
            if value and not value in newvals:
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
    
dc = Namespace("http://purl.org/dc/terms/")
auth = Namespace("http://vocab.rpi.edu/auth/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")
prov  = Namespace("http://www.w3.org/ns/prov#")
            
class User(MappedResource, UserMixin):
    rdf_type = prov.Agent

    key = 'id'

    id = single(dc.identifier)
    active = single(auth.active)
    confirmed_at = single(auth.confirmed)
    email = single(auth.email)
    current_login = single(auth.hadCurrentLogin)
    current_login_ip = single( auth.hadCurrentLoginIP)
    last_login_at = single( auth.hadLastLogin)
    hadLastLoginIP = single( auth.hadLastLoginIP)
    hadLoginCount = single( auth.hadLoginCount)
    roles = multiple( auth.hasRole)
    password = single( auth.passwd)
    familyName = single(foaf.familyName)
    givenName = single(foaf.givenName)



###  http://www.w3.org/ns/prov#Role

class Role(MappedResource, RoleMixin):
    rdf_type = prov.Role
    name = single(RDFS.label)
    key = 'name'

class WhyisDatastore(Datastore):

    def __init__(self, db, classes, prefix):
        Datastore.__init__(self, db)
        db.datastore = self
        self.db = db
        self.classes = classes
        self.prefix = prefix

    def commit(self):
        self.db.commit()

    @tag_datastore
    def put(self, model):
        #self.db.add(model)
        self.update(model.graph, model.identifier)
        return model

    def delete(self, model):
        self.delete(model.identifier)

    @tag_datastore
    def get(self,resUri):
        #print resUri, 'a', [x for x in self.db.objects(resUri,rdfalchemy.RDF.type)]
        for t in self.db.objects(resUri,RDF.type):
            if str(t) in self.classes:
                result = self.classes[t](self.db, resUri)
                result.datasource = self
                return result
        return Resource(self.db, resUri)

    def find(self, model, **kwargs):
        rdf_type = model.rdf_type
        predicates = [(model.__dict__[key].predicate, key) for key, value in kwargs.items()]
        query = ''' select ?identifier where {
        ?identifier a %s;
        ''' % rdf_type + '\n'.join(['    %s ?%s;' % x for x in predicates]) + '''
        .
        }'''
        return self.db.query(query, initBindings=kwargs)

    def read(self, uri):
        db = ConjunctiveGraph(self.db.store)
        idb = Graph(self.db.store,uri) 
        result = Graph(identifier=uri)
        # raise RuntimeError(result)
        result += idb
        describe(db.store, uri, result)
        result.template = None
        if len(self.view_template) > 0:
            result.template = self.view_template[0].value
        return result

    def update(self,inputGraph, uri):
        allGraphs = ConjunctiveGraph(self.db.store)
        allGraphs.remove((uri,None,None))
        idb = Graph(self.db.store,uri)
        idb.remove((None,None,None))
        idb += inputGraph
        idb.template = None
        self.db.store.commit()
        return idb

    def delete(self,uri):
        idb = ConjunctiveGraph(self.db.store,uri)
        if len(idb) == 0:
            abort(404, "Resource does not exist or is not deletable.")
        idb.remove((None,None,None))
        g = ConjunctiveGraph(self.db.store)
        g.remove((uri,None,None))
        g.remove((None,None,uri))
            

class WhyisUserDatastore(WhyisDatastore, UserDatastore):
    def __init__(self, db, classes, prefix):
        c = dict(classes)
        c[User.rdf_type] = User
        c[Role.rdf_type] = Role
        self.User = User
        self.Role = Role
        self.User.prefix = Namespace(prefix+'/user/')
        self.Role.prefix = Namespace(prefix+'/role/')
        WhyisDatastore.__init__(self, db, classes, prefix)
        UserDatastore.__init__(self, User, Role)

    @tag_datastore
    def get_user(self, identifier):
        if isinstance(identifier, URIRef):
            return self.get(identifier)
        for attr in [dc.identifier, auth.email]:
            uri = self.db.value(predicate=attr, object=Literal(identifier))
            if uri is not None:
                self.get(uri)

    def _is_numeric(self, value):
        try:
            int(value)
        except ValueError:
            return False
        return True

    @tag_datastore
    def find_user(self, **kwargs):
        if 'identifier' in kwargs:
            return self.get(URIRef(kwargs['identifier']))
        try:
            u = self.find(User, **kwargs)
        except:
            return None

    @tag_datastore
    def find_role(self, role_name, **kwargs):
        return self.get(self.Role.prefix[role_name])
