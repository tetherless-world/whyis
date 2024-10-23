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


class SETLMaker(UpdateChangeService):
    activity_class = setl.Planner

    def getInputClass(self):
        return pv.File

    def getOutputClass(self):
        return setl.SETLedFile
        
    def process_nanopub(self, i, o, new_np):
        print(i.identifier)
        p = flask.current_app.NS.prov.used
        for script, np, parameterized_type, type_assertion in flask.current_app.db.query('''
select distinct ?setl_script ?np ?parameterized_type ?type_assertion where {
    graph ?type_assertion { ?resource rdf:type ?parameterized_type. }
    ?type_np a np:Nanopublication; np:hasAssertion ?type_assertion.
    minus {
        ?type_assertion prov:wasGeneratedBy [ a setl:Planner].
    }
    graph ?assertion {
      ?setl_script rdfs:subClassOf setl:SemanticETLScript;
        rdfs:subClassOf [ a owl:Restriction;
            owl:onProperty prov:used;
            owl:someValuesFrom ?parameterized_type
      ].
    }
    ?np np:hasAssertion ?assertion; a np:Nanopublication.
    minus {
        ?assertion prov:wasGeneratedBy [ a setl:Planner].
    }
    minus {
        ?planned_assertion prov:wasDerivedFrom ?assertion;
           prov:wasGeneratedBy [ a setl:Planner].
        graph ?planned_assertion {
            ?setl_run a ?setl_script.
            ?extract prov:used ?resource.
        }
    }
}''', initBindings=dict(resource=i.identifier), initNs=flask.current_app.NS.prefixes):
            nanopub = flask.current_app.nanopub_manager.get(np)
            print("Template NP", nanopub.identifier, len(nanopub))
            template_prefix = nanopub.assertion.value(script, setl.hasTemplatePrefix)
            replacement_prefix = flask.current_app.NS.local['setl/' + create_id() + "/"]

            mappings = {}
            for x, in nanopub.assertion.query("select ?x where {?x a ?t}",
                                              initBindings={'t': parameterized_type},
                                              initNs=flask.current_app.NS.prefixes):
                mappings[x] = i.identifier

            script_run = rdflib.URIRef(script.replace(template_prefix, replacement_prefix, 1))
            for x, in nanopub.assertion.query("select ?x where {?x a ?t}",
                                              initBindings={'t': script},
                                              initNs=flask.current_app.NS.prefixes):
                mappings[x] = script_run

            def replace(x):
                if x in mappings:
                    return mappings[x]
                if isinstance(x, rdflib.URIRef) and x.startswith("bnode:"):
                    return rdflib.BNode(x.replace("bnode:", "", 1))
                if isinstance(x, rdflib.URIRef) and x == script:
                    return script
                if isinstance(x, rdflib.URIRef) and x.startswith(template_prefix):
                    return rdflib.URIRef(x.replace(template_prefix, replacement_prefix, 1))
                return x

            for s, p, o in nanopub.assertion:
                new_np.assertion.add((replace(s), replace(p), replace(o)))
            new_np.assertion.add((script_run, rdflib.RDF.type, script))
            new_np.assertion.add((script_run, rdflib.RDF.type, setl.SemanticETLScript))
            new_np.provenance.add((new_np.assertion.identifier, prov.wasDerivedFrom, nanopub.assertion.identifier))
            new_np.provenance.add((new_np.assertion.identifier, prov.wasDerivedFrom, type_assertion))
            print("Instance NP", new_np.identifier, len(new_np))
#            print new_np.serialize(format="trig")
