from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

import itertools

from .global_change_service import GlobalChangeService
from nanopub import Nanopublication
from datastore import create_id
import flask
from flask import render_template
from flask import render_template_string
import logging

import sys, traceback

import database

import tempfile

from depot.io.interfaces import StoredFile

from whyis.namespace import *


class CacheUpdater(GlobalChangeService):
    activity_class = setl.CacheUpdate

    query = None

    classes_and_views = None

    def getInputClass(self):
        return rdflib.RDFS.Resource

    def getOutputClass(self):
        return whyis.CachedResource

    def get_query(self):
        if self.app.cache and self.query is None:
            self.classes_and_views = [x.asdict() for x in self.app.vocab.query('''
select ?class ?view where {
    ?viewProp a <http://vocab.rpi.edu/whyis/CachedView> .
    ?class rdfs:subClassOf* ?c.
    ?c ?viewProp [].
    ?viewProp <http://purl.org/dc/terms/identifier> ?view.
}''')]
            print(self.classes_and_views)
            self.views_by_class = {}
            for cv in self.classes_and_views:
                if cv['class'] not in self.views_by_class:
                    self.views_by_class['class'] = []
                self.views_by_class['class'].append(cv['view'])
            self.query = '''
select distinct ?resource where {
    ?resource rdf:type/rdfs:subClassOf* ?type.
} values ?type { %s }
''' % ' '.join([cv['class'].n3() for cv in self.classes_and_views])
        return self.query

    def process(self, i, o):
        if self.app.cache is None:
            return
        types = [x for x, in i.graph.query('''
select ?type where {
    ?resource rdf:type/rdfs:subClassOf* ?type.
}''',initNs={'rdfs':rdflib.RDFS,'rdf':rdflib.RDF}, initBindings={'resource':i.identifier})]
        views = [self.views_by_class[x] for x in types if x in self.views_by_class]
        views = set(itertools.chain.from_iterable(views))
        for view in views:
            print ("Cacheing",i.identifier, view)
            result, response, headers = self.app.render_view(i.identifier, view,
                                                             use_cache=False)
            if response == 200:
                self.app.cache.set(str((str(resource),view)), (result, headers))
