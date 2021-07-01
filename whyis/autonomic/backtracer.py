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
import re

from depot.io.interfaces import StoredFile

from whyis.namespace import *

class BackTracer(GlobalChangeService):
    def __init__(self, reference, antecedent, consequent, explanation, resource="?resource", rule="<http://vocab.rpi.edu/whyis/Rule>", prefixes=None): 
        if resource is not None:
            self.resource = resource
        self.prefixes = {}
        if prefixes is not None:
            self.prefixes = prefixes
        self.reference = reference
        self.rule = rule
        self.antecedent = antecedent
        self.consequent = consequent
        self.explanation = explanation

    def getInputClass(self):
        return pv.File
    def getOutputClass(self):
        return whyis.InferencedOver

    def get_query(self):
        self.app.db.store.nsBindings = {}
        return '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sets: <http://purl.org/ontology/sets/ont#>
SELECT DISTINCT %s WHERE {
    GRAPH ?g1 { %s }
    GRAPH ?g2 { %s }
    FILTER NOT EXISTS {
    GRAPH ?g1 { %s }
    GRAPH ?g2 { %s }
        ?g2 sets:hypothesis 
            [ a sets:Hypothesis , %s ; 
                rdfs:label "%s" ; 
                sets:antecedentGraph ?g1 ] .
    }
}''' % ( self.resource, self.antecedent, self.consequent, self.antecedent, self.consequent, self.rule, self.reference )

    def query_to_context(self, query_string) :
        string_list = re.split("\s+",query_string)

        new_list = []
        for word in string_list :
            if len(word) > 0 :
                if word[0]=='?':
                    new_list.append("{{"+word[1:]+"}}")
                else :
                    new_list.append(word)

        updated_query_string = ' '.join(new_list)
        return updated_query_string

    def get_context(self, i):
        context = {}
        context_vars = self.app.db.query('''
SELECT DISTINCT * WHERE {
    GRAPH ?g1 { %s }
    GRAPH ?g2 { %s }
    FILTER(regex(str(%s), "^(%s)")) .
}''' % ( self.antecedent, self.consequent, self.resource, i.identifier), initNs=self.prefixes)
        for key in context_vars.vars :
            context[key] = context_vars.bindings[0][key]
        return context

    def process(self, i, o):
        for profile in self.app.config["active_profiles"] :
            if self.reference in self.app.config["reasoning_profiles"][profile] :
                npub = Nanopublication(store=o.graph.store)
                triples = self.app.db.query(
                    '''
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX sets: <http://purl.org/ontology/sets/ont#>
CONSTRUCT {
    ?g2 sets:hypothesis
        [ a sets:Hypothesis , %s ; 
            rdfs:label "%s" ; 
            sets:antecedentGraph ?g1 
        ]  .
} WHERE {
    GRAPH ?g1 { %s }
    GRAPH ?g2 { %s }
    FILTER NOT EXISTS {
        ?g2 sets:hypothesis 
            [ a sets:Hypothesis , %s ; 
                rdfs:label "%s" ; 
                sets:antecedentGraph ?g1 
            ] .
    }
    FILTER (regex(str(%s), "^(%s)"))
}''' % ( self.rule, self.reference, self.antecedent, self.consequent, self.rule, self.reference, self.resource, i.identifier), initNs=self.prefixes)
                try :
                    for s, p, o in triples:
                        print("BackTracer Adding ", s, p, o)
                        npub.assertion.add((s, p, o))
                except :
                    for s, p, o, c in triples:
                        print("BackTracer Adding ", s, p, o)
                        npub.assertion.add((s, p, o))
                #npub.provenance.add((npub.assertion.identifier, prov.value,
                #                     rdflib.Literal(flask.render_template_string(self.explanation, **self.get_context(i)))))

    def __str__(self):
        return "Back Tracer Instance: " + str(self.__dict__)




