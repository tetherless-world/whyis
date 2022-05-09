from builtins import str
import sadi
import setlr
import sdd2rdf
import rdflib
from sdd2rdf import sdd2setl
from datetime import datetime

from .global_change_service import GlobalChangeService
from whyis.nanopub import Nanopublication
from whyis.datastore import create_id
import flask
from flask import render_template
from flask import render_template_string
import logging

import sys, traceback


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
        values = self.app.db.query('''
SELECT ?prefix ?sdd_file ?data_file ?content_type ?delimiter ?dataset
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
''', initBindings={"sdd_file": i.identifier}, initNs=NS.prefixes)
        for prefix, sdd_file, data_file, content_type, delimiter, dataset in values:
            resource = self.app.get_resource(sdd_file)
            fileid = resource.value(self.app.NS.whyis.hasFileID)
            if fileid is not None:
                sdd_data = self.app.file_depot.get(fileid.value)
            else:
                sdd_data = sdd_file

            output = sdd2setl(sdd_data,
                              prefix.value,
                              data_file,
                              content_type.value,
                              delimiter.value,
                              None,
                              None,
                              dataset)
            npub = Nanopublication()
            npub.assertion.parse(data=output, format="turtle")

            sdd_setl = npub.assertion.value(predicate=rdflib.RDF.type, object=setl.SemanticETLScript)
            npub.assertion.add((sdd_setl, prov.wasDerivedFrom, sdd_file))
            new_nps = self.app.nanopub_manager.prepare(npub)
            self.app.nanopub_manager.publish(*new_nps)
