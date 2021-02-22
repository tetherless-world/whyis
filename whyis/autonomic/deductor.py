from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from .global_change_service import GlobalChangeService
from .update_change_service import UpdateChangeService
from nanopub import Nanopublication
from datastore import create_id
import flask
from flask import render_template
from flask import render_template_string
import logging

#try:
#    import config.Config as Config
#except:
#    from whyis import config_defaults.Config as Config

import sys, traceback

import database

import tempfile

from depot.io.interfaces import StoredFile

from whyis.namespace import *

class Deductor(GlobalChangeService):
    def __init__(self, reference, antecedent, consequent, explanation, resource="?resource", prefixes=None): 
        if resource is not None:
            self.resource = resource
        self.prefixes = {}
        if prefixes is not None:
            self.prefixes = prefixes
        self.reference = reference
        self.antecedent = antecedent
        self.consequent = consequent
        self.explanation = explanation

    def getInputClass(self):
        return pv.File

    def getOutputClass(self):
        return whyis.InferencedOver

    def get_query(self):
        self.app.db.store.nsBindings = {}
        return '''SELECT DISTINCT %s WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\n}''' % (
        self.resource, self.antecedent, self.consequent)

    def get_context(self, i):
        context = {}
        context_vars = self.app.db.query('''SELECT DISTINCT * WHERE {\n%s \nFILTER(regex(str(%s), "^(%s)")) . }''' % (
        self.antecedent, self.resource, i.identifier), initNs=self.prefixes)
        for key in context_vars.vars :
            context[key] = context_vars.bindings[0][key]
        return context

    def process(self, i, o):
        for profile in self.app.config["active_profiles"] :
            if self.reference in self.app.config["reasoning_profiles"][profile] :
                npub = Nanopublication(store=o.graph.store)
                triples = self.app.db.query(
                    '''CONSTRUCT {\n%s\n} WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\nFILTER (regex(str(%s), "^(%s)")) .\n}''' % (
                    self.consequent, self.antecedent, self.consequent, self.resource, i.identifier), initNs=self.prefixes)
                try :
                    for s, p, o in triples:
                        print("Deductor Adding ", s, p, o)
                        npub.assertion.add((s, p, o))
                except :
                    for s, p, o, c in triples:
                        print("Deductor Adding ", s, p, o)
                        npub.assertion.add((s, p, o))                
                npub.provenance.add((npub.assertion.identifier, prov.value,
                                     rdflib.Literal(flask.render_template_string(self.explanation, **self.get_context(i)))))

    def __str__(self):
        return "Deductor Instance: " + str(self.__dict__)

