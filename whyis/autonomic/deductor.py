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


class Deductor(UpdateChangeService):
    def __init__(self, where, construct, explanation, resource="?resource", prefixes=None):  # prefixes should be
        if resource is not None:
            self.resource = resource
        self.prefixes = {}
        if prefixes is not None:
            self.prefixes = prefixes
        self.where = where
        self.construct = construct
        self.explanation = explanation

    def getInputClass(self):
        return pv.File  # input and output class should be customized for the specific inference

    def getOutputClass(self):
        return setl.SETLedFile

    def get_query(self):
        self.app.db.store.nsBindings = {}
        return '''SELECT DISTINCT %s WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\n}''' % (
        self.resource, self.where, self.construct)

    def get_context(self, i):
        context = {}
        context_vars = self.app.db.query('''SELECT DISTINCT * WHERE {\n%s \nFILTER(regex(str(%s), "^(%s)")) . }''' % (
        self.where, self.resource, i.identifier), initNs=self.prefixes)
        # print(context_vars)
        for key in list(context_vars.json["results"]["bindings"][0].keys()):
            context[key] = context_vars.json["results"]["bindings"][0][key]["value"]
        return context

    def process(self, i, o):
        npub = Nanopublication(store=o.graph.store)
        triples = self.app.db.query(
            '''CONSTRUCT {\n%s\n} WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\nFILTER (regex(str(%s), "^(%s)")) .\n}''' % (
            self.construct, self.where, self.construct, self.resource, i.identifier), initNs=self.prefixes)
        for s, p, o, c in triples:
            print("Deductor Adding ", s, p, o)
            npub.assertion.add((s, p, o))
        npub.provenance.add((npub.assertion.identifier, prov.value,
                             rdflib.Literal(flask.render_template_string(self.explanation, **self.get_context(i)))))

    def __str__(self):
        return "Deductor Instance: " + str(self.__dict__)
