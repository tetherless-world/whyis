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

class Deductor(GlobalChangeService):
    def __init__(self, antecedent, consequent, explanation, resource="?resource", prefixes=None): 
        if resource is not None:
            self.resource = resource
        self.prefixes = {}
        if prefixes is not None:
            self.prefixes = prefixes
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
        # print(context_vars)
        #for key in list(context_vars.json["results"]["bindings"][0].keys()):
        #    context[key] = context_vars.json["results"]["bindings"][0][key]["value"]
        for key in context_vars.vars :
            context[key] = context_vars.bindings[0][key]
        return context

    def process(self, i, o):
        npub = Nanopublication(store=o.graph.store)
        triples = self.app.db.query(
            '''CONSTRUCT {\n%s\n} WHERE {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\nFILTER (regex(str(%s), "^(%s)")) .\n}''' % (
            self.consequent, self.antecedent, self.consequent, self.resource, i.identifier), initNs=self.prefixes)
        for s, p, o in triples:
            print("Deductor Adding ", s, p, o)
            npub.assertion.add((s, p, o))
        npub.provenance.add((npub.assertion.identifier, prov.value,
                             rdflib.Literal(flask.render_template_string(self.explanation, **self.get_context(i)))))

    def __str__(self):
        return "Deductor Instance: " + str(self.__dict__)

'''class Deduct(GlobalChangeService):
    def process(self, i, o):
        for profile in config.Config["active_profiles"] :
            for inference_rule in config.Config["reasoning_profiles"][profile] :
                try :
                    deductor_instance = autonomic.Deductor(
                        resource = config.Config["axioms"][inference_rule]["resource"] ,
                        prefixes = config.Config["axioms"][inference_rule]["prefixes"] ,
                        antecedent = config.Config["axioms"][inference_rule]["antecedent"] ,
                        consequent = config.Config["axioms"][inference_rule]["consequent"] ,
                        explanation = inference_rule + ": " + config.Config["axioms"][inference_rule]["explanation"]
                )
                except Exception as e:
                    if hasattr(e, 'message'):
                        print("Error creating deductor instance: " + e.message)
                    else:
                        print("Error creating deductor instance: " + e)
                try :
                    deductor_instance.app = self.app
                    deductor_instance.process_graph(self.app.db)
                except Exception as e:
                    if hasattr(e, 'message'):
                        print("Error processing graph: " + e.message)
                    else:
                        print("Error processing graph: " + e)
'''
