from __future__ import print_function
from __future__ import absolute_import
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring
from builtins import object
from rdflib import *
from rdflib.resource import *
import rdflib
from . import mimeparse
import collections
import sys
from uuid import uuid4
from webob import Request
from .utils import create_id
from threading import Thread
import urllib.request, urllib.error, urllib.parse
from werkzeug.wrappers import BaseResponse as Response

from .serializers import *

from io import StringIO

rdflib.plugin.register('sparql', rdflib.query.Processor,
                       'rdfextras.sparql.processor', 'Processor')
rdflib.plugin.register('sparql', rdflib.query.Result,
                       'rdfextras.sparql.query', 'SPARQLQueryResult')

dc = Namespace("http://purl.org/dc/terms/")
mygrid = Namespace("http://www.mygrid.org.uk/mygrid-moby-service#")
nanopub = Namespace("http://www.nanopub.org/nschema#")

# Install required libraries using easy_install:
# sudo easy_install 'rdflib>=3.0' surf rdfextras surf.rdflib

NS = Namespace("")

def _skolemize():
    '''Creates a simple generator for UUID4 IDs.'''
    return NS[uuid4().hex]

class Individual(Resource):
    class item(object):
        def __init__(self, subject, predicate):
            self._subject = subject
            self._predicate = predicate
        def __iter__(self):
            for o in self._subject.objects(self._predicate):
                if isinstance(o,Literal): yield o.value
                else: yield o
        def remove(self,o):
            if not isinstance(o,rdflib.term.Identifier) and isinstance(o,Literal):
                o = Literal(o)
            self._subject.remove(self._predicate,o)
        def append(self,o):
            if not isinstance(o,rdflib.term.Identifier) and not isinstance(o,Literal):
                o = Literal(o)
            self._subject.add(self._predicate,o)
        # def __iadd__(self, l):
        #     for o in l:
        #         self.append(o)
        # def __isub__(self, l):
        #     for o in l:
        #         self.remove(o)
    # def __getitem__(self, predicate):
    #     return self.item(self,predicate)
    # def __setitem__(self, predicate, o):
    #     if not isinstance(o,rdflib.term.Identifier) and not isinstance(o,Literal):
    #         o = Literal(o)
    #     self.set(predicate,o)

class OntClass(Resource):
    def __init__(self,graph, identifier=None):
        if isinstance(identifier, basestring):
            identifier = URIRef(identifier)
        Resource.__init__(self,graph,identifier)
    def __call__(self,identifier=None):
        if isinstance(identifier, basestring):
            identifier = URIRef(identifier)
        if identifier == None:
            identifier = BNode()
        result = Resource(self.graph,identifier)
        result.add(RDF.type,self.identifier)
        return result
    def all(self):
        for x in self.graph[:RDF.type:self.identifier]:
            yield Resource(self.graph,x)

class HTTPError(Exception):
    def __init__(self, status):
        self.value = status
    def __str__(self):
        return repr(self.value)
            
class IncompleteError(Exception):
    def __init__(self):
        self.value = "302 Moved Temporarily"
    def __str__(self):
        return repr(self.value)

class SADIGraph(ConjunctiveGraph):
    attachments = {}

    def get(self, uri, accept=None):
        try:
            if accept != None:
                raise Exception()
            message = self.attachments[str(uri)]
            data = message.get_payload(decode=True)
            mimetype = message.get_content_type()
            return Response(data,mimetype=mimetype)
        except:
            headers = {}
            if accept != None:
                headers['Accept'] = accept
            request = urllib.request.Request(str(uri),headers=headers)
            response = urllib.request.urlopen(request)
            info = response.info()
            data = response.read()
            mimetype = info.getheader("Content-Type")
            return Response(data,mimetype=mimetype)

contentTypes = {}
contentTypes.update({
            None:DefaultSerializer('xml'),
            "application/rdf+xml":DefaultSerializer('xml'),
            "text/rdf":DefaultSerializer('xml'),
            'multipart/related': MultipartSerializer(contentTypes),
            'application/x-www-form-urlencoded':DefaultSerializer('xml'),
            'text/turtle':DefaultSerializer('n3','turtle'),
            'application/x-turtle':DefaultSerializer('n3','turtle'),
            'text/plain':DefaultSerializer('nt'),
            'text/n3':DefaultSerializer('n3'),
            'text/html':RDFaSerializer(),
            'application/json':JSONSerializer(),
            'application/ld+json':JsonLdSerializer(),
            'text/csv':CSVSerializer(','),
            'text/comma-separated-values':CSVSerializer(','),
            'text/tab-separated-values':CSVSerializer('\t'),
    })

def getFormat(contentType):
    if contentType == None:
        return [ "application/rdf+xml",contentTypes[None]]
    type = mimeparse.best_match(["application/rdf+xml"]+[x for x in list(contentTypes.keys()) if x != None],
                                contentType)
    if type == '' or type == None: 
        return ["application/rdf+xml",DefaultSerializer('xml')]
    else:
        return [type,contentTypes[type]]

def deserialize(graph, content, mimetype):
    f = getFormat(mimetype)
    f[1].deserialize(graph,content,mimetype)

def serialize(graph, accept):
    f = getFormat(accept)
    return f[1].serialize(graph)

class Service(object):
    serviceDescription = None

    comment = None
    serviceDescriptionText = None
    serviceNameText = None
    label = None
    name = None
    results = {}
    active_tasks = {}
    attachments = {}

    def __init__(self):
        self.contentTypes = contentTypes
        #self.contentTypes['multipart/related'] = MultipartSerializer(self.contentTypes)


    def getFormat(self, contentType):
        return getFormat(contentType)

    def deserialize(self, graph, content, mimetype):
        deserialize(graph,content,mimetype)

    def serialize(self, graph, accept):
        return serialize(graph, accept)

    def get(self, uri, i, accept=None):
        return i.graph.get(uri, accept)

    def annotateServiceDescription(self, desc):
        pass

    def getOutputClass(self):
        return self.output_class

    def getInputClass(self):
        return self.input_class

    input_class = OWL.Thing

    output_class = OWL.Thing

    def getServiceDescription(self):
        if self.serviceDescription == None:
            self.serviceDescription = Graph()
            self.Description = OntClass(self.serviceDescription,mygrid.serviceDescription)
            self.Organization = OntClass(self.serviceDescription,mygrid.organisation)
            self.Operation = OntClass(self.serviceDescription,mygrid.operation)
            self.Parameter = OntClass(self.serviceDescription,mygrid.parameter)

            self.inputClass = self.getInputClass()
            self.outputClass = self.getOutputClass()
            
            desc = self.Description("#")

            if self.label is not None:
                desc.add(RDFS.label, Literal(self.label))
            if self.comment is not None:
                desc.add(RDFS.comment, Literal(self.comment))
            if self.serviceDescriptionText is not None:
                desc.add(mygrid.hasServiceDescriptionText, Literal(self.serviceDescriptionText))
            if self.serviceNameText is not None:
                desc.add(mygrid.hasServiceNameText, Literal(self.serviceNameText))
            desc.add(mygrid.providedBy, self.getOrganization())
            
            desc.add(mygrid.hasOperation, self.Operation("#operation"))

            outputParameter = self.Parameter("#output")
            desc.value(mygrid.hasOperation).add(mygrid.outputParameter, outputParameter)
            outputParameter.add(mygrid.objectType, self.outputClass)

            inputParameter = self.Parameter("#input")
            desc.value(mygrid.hasOperation).add(mygrid.inputParameter, inputParameter)
            inputParameter.add(mygrid.objectType, self.inputClass)

            if "getParameterClass" in dir(self):
                self.parameterClass = self.getParameterClass()
                secondaryParameter = self.Parameter("#params")
                desc.value(mygrid.hasOperation).add(mygrid.secondaryParameter, secondaryParameter)
                secondaryParameter.add(mygrid.objectType, self.parameterClass)

            operation = desc.value(mygrid.hasOperation)
            operation.add(mygrid.outputParameter, outputParameter)
            operation.add(mygrid.inputParameter, inputParameter)

            self.annotateServiceDescription(desc)

        return self.serviceDescription

    def getInstances(self, graph):
        InputClass = OntClass(graph,self.getInputClass())
        instances = InputClass.all()
        return instances

    def makeOutputInstance(self,i):
        outputGraph = Graph()
        OutputClass = OntClass(outputGraph,self.getOutputClass())
        o = OutputClass(i.identifier)
        return o

    def explain(self, i, o, provenance, pubinfo):
        pass

    def processGraph(self,content, type):
        inputGraph = SADIGraph()
        self.deserialize(inputGraph, content, type)
        outputGraph = ConjunctiveGraph()

        instances = self.getInstances(inputGraph)
        for i in instances:
            pub = outputGraph.resource(_skolemize())
            pub.add(RDF.type, nanopub.Nanopublication)
            assertion = Graph(outputGraph.store, pub.identifier+"_assertion")
            pub.add(nanopub.hasAssertion, assertion.identifier)
            OutputClass = OntClass(assertion,self.getOutputClass())
            o = OutputClass(i.identifier)
            self.process(i, o)
            provenance = Graph(outputGraph.store, pub.identifier+"_provenance")
            pub.add(nanopub.hasProvenance, provenance.identifier)
            pubinfo = Graph(outputGraph.store, nanopub.identifier+"_pubinfo")
            pub.add(nanopub.hasPublicationInfo, pubinfo.identifier)
            self.explain(i, o, provenance.resource(i), pubinfo.resource(i))
        return outputGraph

    def defer(self, i, task):
        o = self.makeOutputInstance(i)
        def fn():
            self.async_process(i,o)
            self.results[task] = o.graph
            del self.active_tasks[task]
        thread = Thread(target=fn)
        thread.daemon = True
        self.active_tasks[task] = thread
        thread.start()

    def result(self,task):
        try:
            return self.results[task]
        except:
            if task in self.active_tasks:
                raise IncompleteError()
        raise HTTPError('404 Not Found')

    def process(self, i, o):
        task = URIRef(self.request.url+"?task="+create_id())
        self.defer(i, task)
        o.add(RDFS.isDefinedBy,task)
        self.status = '202 Accepted'

    def GET(self, environ, start_response):
        request = Request(environ,'utf-8')
        acceptType = self.getFormat(environ.get('HTTP_ACCEPT'))
        response_headers = [
            ('Content-type', acceptType[0]+'; charset=utf-8'),
            ('Access-Control-Allow-Origin','*')
        ]
        status = None
        graph = None
        if 'task' in request.params:
            task = URIRef(request.url)
            try:
                graph = self.result(task)
                status = '200 OK'
            except IncompleteError:
                status = '302 Moved Temporarily'
                response_headers = [
                    ('Pragma','sadi-please-wait = 5000'),
                    ('Location',str(task))
                ]
        else:
            graph = self.getServiceDescription()
            status = '200 OK'
        start_response(status, response_headers)
        self.request = None
        if graph != None:
            return [self.serialize(graph,acceptType[0])]
        else:
            return []

    def POST(self, environ, start_response):
        self.request = Request(environ,'utf-8')
        self.status = '200 OK'
        acceptType = self.getFormat(self.request.headers.get('Accept'))
        response_headers = [
            ('Content-type', acceptType[0]+'; charset=utf-8'),
            ('Access-Control-Allow-Origin','*')
        ]
        content = str(self.request.body,'utf-8')
        graph = self.processGraph(content, self.request.headers['Content-Type'])
        start_response(self.status, response_headers)
        self.request = None
        return [self.serialize(graph,acceptType[0])]

    def __call__(self,environ,start_response):
        method = environ['REQUEST_METHOD']
        if method == 'GET':
            return self.GET(environ,start_response)
        if method == 'POST':
            return self.POST(environ,start_response)
        status = '405 Method Not Allowed'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return ['Error 405: Method Not Allowed']

def setup_test_client(app):
    from werkzeug.test import Client
    from werkzeug.wrappers import BaseResponse
    import werkzeug.wrappers
    class Response(BaseResponse, werkzeug.wrappers.CommonResponseDescriptorsMixin):
        pass 
    c = Client(app,Response)
    return c
    
def serve(resource,port):
    from wsgiref.simple_server import make_server

    httpd = make_server('', port, resource)
    print("Serving HTTP on port",port,"...")

    # Respond to requests until process is killed
    httpd.serve_forever()

