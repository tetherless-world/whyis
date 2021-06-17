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

import sys, traceback

import database

import tempfile

from depot.io.interfaces import StoredFile

from whyis.namespace import *

class ChainTracer(GlobalChangeService):
    def __init__(self, rule_dictionary): 
        if rule_dictionary is not None:
            self.rule_dictionary = rule_dictionary

    def getInputClass(self):
        return pv.File

    def getOutputClass(self):
        return whyis.InferencedOver

    def get_query(self):
        self.app.db.store.nsBindings = {}
        return '''PREFIX whyis: <http://vocab.rpi.edu/whyis/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> SELECT DISTINCT %s WHERE {\n\tGRAPH ?g1 { %s }\n?g1 whyis:hypothesis [\n\ta whyis:Hypothesis , ?h1 ] .\nGRAPH ?g2 { %s }\n?g2 whyis:hypothesis [\n\ta whyis:Hypothesis , h2 ] .\nFILTER NOT EXISTS {\n\t?g2 whyis:chainHypothesis [ ?h1 ?h2] . \n\t} \n}''' % (
        self.resource, self.antecedent, self.consequent)

    def get_context(self, i):
        context = {}
        context_vars = self.app.db.query('''SELECT DISTINCT * WHERE {\n%s \nFILTER(regex(str(%s), "^(%s)")) . }''' % (
        self.antecedent, self.resource, i.identifier), initNs=self.prefixes)
        for key in context_vars.vars :
            context[key] = context_vars.bindings[0][key]
        return context

    def process(self, i, o):
        npub = Nanopublication(store=o.graph.store)
        for profile in self.app.config["active_profiles"] :
            for rule_reference in self.app.config["reasoning_profiles"][profile] :
                for rule in rule_dictionary :
                    if rule_dictionary[rule]["reference"] == rule_reference :
                        triples = self.app.db.query(
                            '''PREFIX whyis: <http://vocab.rpi.edu/whyis/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> CONSTRUCT {\n?g2 whyis:chainHypothesis [ ?h1 ?h2 ]  . \n} WHERE {\n\tGRAPH ?g1 { %s }\n?g1 whyis:hypothesis [\n\ta whyis:Hypothesis , ?h1 ] .\nGRAPH ?g2 { %s }\n?g2 whyis:hypothesis [\n\ta whyis:Hypothesis , h2 ] .\nFILTER NOT EXISTS {\n\t?g2 whyis:chainHypothesis [ ?h1 ?h2] . \n\t} \n}\n}''' % (
                        rule["antecedent"], rule["consequent"], rule["resource"]), initNs=rule["prefixes"])
                        try :
                            for s, p, o in triples:
                                print("ChainTracer Adding ", s, p, o)
                                npub.assertion.add((s, p, o))
                        except :
                            for s, p, o, c in triples:
                                print("ChainTracer Adding ", s, p, o)
                                npub.assertion.add((s, p, o))


    def __str__(self):
        return "Chain Tracer Instance: " + str(self.__dict__)




