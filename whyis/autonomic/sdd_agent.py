from builtins import str
import sadi
import rdflib
import setlr
import sdd2rdf
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
prefix example-kb: <http://example.com/kb/example/> 
prefix sdd: <http://purl.org/twc/sdd/> 
prefix ov: <http://open.vocab.org/terms/> 
prefix void: <http://rdfs.org/ns/void#> 
prefix dcterms: <http://purl.org/dc/terms/> 
prefix dcat: <http://www.w3.org/ns/dcat#> 
prefix csvw: <http://www.w3.org/ns/csvw#>
prefix whyis: <http://vocab.rpi.edu/whyis/>

SELECT ?prefix ?sdd_file ?data_file ?content_type ?delimiter
WHERE {
?sdd_file rdf:type sdd:SemanticDataDictionary .

?data_file dcterms:conformsTo ?sdd_file ;
    ov:hasContentType ?content_type ;
    csvw:delimiter ?delimiter .

?dataset dcat:distribution ?data_file ;
    void:uriSpace ?prefix .
FILTER NOT EXISTS { ?data_file rdf:type whyis:ProcessedFile . }
}
''')
        output = sdd2setl(values.json["results"]["bindings"][0]["sdd_file"]["value"] + "#InfoSheet",values.json["results"]["bindings"][0]["prefix"]["value"],values.json["results"]["bindings"][0]["data_file"]["value"],values.json["results"]["bindings"][0]["content_type"]["value"],values.json["results"]["bindings"][0]["delimiter"]["value"],'Infosheet')
        #with open('/apps/whyis/out.setl','wb') as out: 
        #    out.write(output.encode('utf8'))
        npub = Nanopublication(store=self.app.db.store)
        npub.assertion.parse(data=output,format="turtle")
        npub.assertion.add((rdflib.URIRef(values.json["results"]["bindings"][0]["data_file"]["value"]), rdflib.RDF.type, whyis.ProcessedFile))
