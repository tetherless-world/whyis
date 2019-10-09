from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from .update_change_service import UpdateChangeService
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

class OverlayGraph(rdflib.Graph):
    def __init__(self, read=None, write=None):
        if read is not None:
            self.read=read
        if write is not None:
            self.write=write

class RLReasoningAgent(UpdateChangeService):
    def __init__(self, closure_bool=False, axiomatic_bool=False, datatype_axiom_bool=False):
        self.closure_bool = closure_bool
        self.axiomatic_bool = axiomatic_bool
        self.datatype_axiom_bool = datatype_axiom_bool

    def getInputClass(self):
        return pv.File  # input and output class should be customized for the specific inference

    def getOutputClass(self):
        return setl.SETLedFile # this should be updated

    def get_query(self):
        return '''SELECT DISTINCT ?s ?p ?o  WHERE {?s ?p ?o . }'''

    def process(self, i, o):
        new_graph = OverlayGraph(read=i.graph, write=o.graph)
        reasoner = owlrl.DeductiveClosure(owlrl.OWLRL_Extension, rdfs_closure = self.closure_bool, axiomatic_triples = self.axiomatic_bool, datatype_axioms = self.datatype_axiom_bool)
        reasoner.expand(new_graph) # run reasoner using specified options

    def __str__(self):
        return "RL Reasoner Instance: " + str(self.__dict__)
