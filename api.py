from rdflib import *
from flask import Flask, request, make_response, render_template, g, session, abort
from flask_restful import Resource, Api
import sadi

def serializer(mimetype):
    def wrapper(graph, code, headers=None):
        data = ''
        print(graph)
        if graph is not None and hasattr(graph, "serialize"):
            data = graph.serialize(format=sadi.contentTypes[mimetype].outputFormat)
        #print data, code, len(graph), mimetype
        resp = make_response(data, code)
        resp.headers.extend(headers or {})
        print(data)
        return resp
    return wrapper

class JsonLDSerializer(sadi.DefaultSerializer):
    context = None
    def serialize(self,graph):
        if self.context != None:
            self.bindPrefixes(graph)
            return graph.serialize(format=self.outputFormat,
                                   context= self.context,encoding='utf-8')



sadi.contentTypes['application/json'] = JsonLDSerializer("json-ld")
sadi.contentTypes['application/ld+json'] = JsonLDSerializer("json-ld")
class LinkedDataApi(Api):

    _local_resources = {}

    def __init__(self, app, api_prefix, store, host_prefix, decorators=[]):
        Api.__init__(self, app, prefix=api_prefix)
        self.store = store
        for mimetype in list(sadi.contentTypes.keys()):
            if mimetype is not None:
                self.representations[mimetype] = serializer(mimetype)

        self.lod_prefix = host_prefix + api_prefix
        self._decorators = decorators

    def __getitem__(self,cl):
        return self._local_resources[cl]

