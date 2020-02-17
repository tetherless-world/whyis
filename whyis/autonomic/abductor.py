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


class Abductor(UpdateChangeService):
    def __init__(self, where, explanation, resource="?resource", prefixes=None): 
        if resource is not None:
            self.resource = resource
        self.prefixes = {}
        if prefixes is not None:
            self.prefixes = prefixes
        self.where = where
        self.construct = construct
        self.explanation = explanation

    def getInputClass(self):
        return pv.File  #should update

    def getOutputClass(self):
        return whyis.InferencedOver 

    def get_query(self):
        self.app.db.store.nsBindings = {}
        return '''SELECT DISTINCT %s WHERE {\n%s %s\n}''' % (
        self.resource, self.where, self.construct)

    def get_context(self, i):
        context = {}
        context_vars = self.app.db.query('''SELECT DISTINCT * WHERE {\n%s %s\nFILTER(regex(str(%s), "^(%s)")) . }''' % (
        self.where, self.construct, self.resource, i.identifier), initNs=self.prefixes)
        for key in list(context_vars.json["results"]["bindings"][0].keys()):
            context[key] = context_vars.json["results"]["bindings"][0][key]["value"]
        return context

    def process(self, i, o):
        npub = Nanopublication(store=o.graph.store)
        graph_obj = self.app.db.query(
            '''SELECT DISTINCT ?g WHERE {GRAPH ?g {\n%s \nFILTER NOT EXISTS {\n%s\n\t}\nFILTER (regex(str(%s), "^(%s)")) .\n}}''' % (
            self.construct, self.resource, i.identifier), initNs=self.prefixes)
        for s, p, o, c in triples:
            print("Abductor Adding ", s, p, o)
            npub.assertion.add((s, p, o))
        npub.provenance.add((graph_obj.identifier, skos.editorialNote,
                             rdflib.Literal(flask.render_template_string(self.explanation, **self.get_context(i)))))
    def __str__(self):
        return "Abductor Instance: " + str(self.__dict__)

class Abduct(GlobalChangeService):
    def process(self, i, o):
        for profile in config.Config["active_profiles"] :
            for inference_rule in config.Config["reasoning_profiles"][profile] :
                try :
                    abductor_instance = autonomic.Abductor(
                        resource = config.Config["axioms"][inference_rule]["resource"] ,
                        prefixes = config.Config["axioms"][inference_rule]["prefixes"] ,
                        where = config.Config["axioms"][inference_rule]["where"] 
                        construct = config.Config["axioms"][inference_rule]["construct"],
                        explanation = "Derived from axiom - " + inference_rule + ": " + config.Config["axioms"][inference_rule]["explanation"]
                )
                except Exception as e:
                    if hasattr(e, 'message'):
                        print("Error creating abductor instance: " + e.message)
                    else:
                        print("Error creating abductor instance: " + e)
                try :
                    abductor_instance.app = self.app
                    abductor_instance.process_graph(self.app.db)
                except Exception as e:
                    if hasattr(e, 'message'):
                        print("Error processing graph: " + e.message)
                    else:
                        print("Error processing graph: " + e)

