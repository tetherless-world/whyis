from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from .update_change_service import UpdateChangeService
from whyis.nanopub import Nanopublication
from whyis.datastore import create_id
import flask
from flask import render_template
from flask import render_template_string
import logging

import sys, traceback

import whyis.database

import tempfile

from depot.io.interfaces import StoredFile

from whyis.namespace import *


class Crawler(UpdateChangeService):
    activity_class = whyis.GraphCrawl

    def __init__(self, depth=-1, predicates=[None], node_type=whyis.CrawlerStart, output_node_type=whyis.Crawled):
        self.depth = depth
        self.node_type = node_type
        self.output_node_type = output_node_type
        self.predicates = predicates

    def getInputClass(self):
        return self.node_type

    def getOutputClass(self):
        return self.output_node_type

    def get_query(self):
        return '''select ?resource where {
    ?resource rdf:type/rdfs:subClassOf* %s.
}''' % self.getInputClass().n3()

    def process(self, i, o):
        cache = set()
        todo = [(i.identifier, self.depth)]
        # this non-recursive form does a BFS of the linked data graph.
        while len(todo) > 0:
            uri, depth = todo.pop()
            # print uri, depth, len(todo)
            if uri in cache:
                continue
            node = None
            node = flask.current_app.get_resource(uri, async_=False)
            cache.add(uri)
            if depth != 0:
                for p in self.predicates:
                    todo.extend([(x.identifier, depth - 1) for x in node[p]])
