from builtins import str
import sadi
import setlr
import sdd2rdf
import rdflib
from sdd2rdf import sdd2setl
from datetime import datetime

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
sdd = rdflib.Namespace("http://purl.org/twc/sdd/")

class SDDAgent(GlobalChangeService):
    activity_class = setl.Planner

    def getInputClass(self):
        return sdd.SemanticDataDictionary

    def getOutputClass(self):
        return setl.SETLedFile

    def get_query(self):
        return '''select distinct ?resource where { ?resource a %s.}''' % self.getInputClass().n3()

    def process(self, i, o):
        values = self.app.db.query('''prefix sio: <http://semanticscience.org/resource/>
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix sdd: <http://purl.org/twc/sdd/>
prefix ov: <http://open.vocab.org/terms/>
prefix void: <http://rdfs.org/ns/void#>
prefix dcterms: <http://purl.org/dc/terms/>
prefix dcat: <http://www.w3.org/ns/dcat#>
prefix csvw: <http://www.w3.org/ns/csvw#>
prefix whyis: <http://vocab.rpi.edu/whyis/>
prefix setl: <http://purl.org/twc/vocab/setl/>
prefix prov:          <http://www.w3.org/ns/prov#>

SELECT ?prefix ?sdd_file ?data_file ?content_type ?delimiter
WHERE {
    ?data_file dcterms:conformsTo ?sdd_file ;
       ov:hasContentType ?content_type ;
       csvw:delimiter ?delimiter .

   ?dataset dcat:distribution ?data_file ;
       void:uriSpace ?prefix .
    MINUS {
        ?setl_script prov:wasDerivedFrom ?sdd_file;
            a setl:SemanticETLScript.
        ?dataset prov:wasGeneratedBy ?setl_script;
            prov:wasGeneratedBy ?template.
        ?template a setl:Transform;
            prov:used/prov:wasGeneratedBy ?extract.
        ?extract a setl:Extract;
            prov:used ?data_file.
    }
}
''', initBindings={"sdd_file": i.identifier})
        for prefix, sdd_file, data_file, content_type, delimiter in values:
            output = sdd2setl(sdd_file + "#InfoSheet",
                              prefix.value,
                              data_file,
                              content_type.value,
                              delimiter.value)
            npub = Nanopublication()
            npub.assertion.parse(data=output, format="turtle")

            sdd_setl = npub.assertion.value(predicate=rdflib.RDF.type, object=setl.SemanticETLScript)
            npub.assertion.add((sdd_setl, prov.wasDerivedFrom, sdd_file))
            new_nps = self.app.nanopub_manager.prepare(npub)
            self.app.nanopub_manager.publish(*new_nps)
