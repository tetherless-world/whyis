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


## TODO: Add content negotiation.
class OntologyImporter(UpdateChangeService):
    activity_class = whyis.OntologyImport

    def get_query(self):
        return '''select ?resource where {
    ?ontology owl:imports ?resource.
}'''

    def getInputClass(self):
        return rdflib.OWL.Ontology

    def getOutputClass(self):
        return whyis.ImportedOntology

    def process_nanopub(self, i, o, new_np):
        if (i.identifier, rdflib.RDF.type, whyis.ImportedOntology) in self.app.db:
            print("Skipping already imported ontology:", i.identifier)
            return
        print("Attempting to import", i.identifier)
        file_format = rdflib.util.guess_format(i.identifier)
        try:  # Try the best guess at a format.
            g = rdflib.Graph()
            g.parse(location=i.identifier, format=file_format, publicID=self.app.NS.local)
            g.serialize()  # to test that parsing was actually successful.
            for s, p, o in g:
                new_np.assertion.add((s, p, o))
            logging.debug("%s was parsed as %s" % (i.identifier, file_format))
            print("%s was parsed as %s" % (i.identifier, file_format))
            print(len(new_np.assertion), len(g))
        except Exception:  # If that doesn't work, brute force it with all possible RDF formats, most likely first.
            print("Could not parse %s as %s" % (i.identifier, file_format))
            # traceback.print_exc(file=sys.stdout)
            parsed = False
            for f in ['xml', 'turtle', 'trig',  # Most likely
                      'n3', 'nquads', 'nt',  # rarely used for ontologies, but sometimes
                      'json-ld',  # occasionally used
                      'hturtle', 'trix',  # uncommon
                      'rdfa1.1', 'rdfa1.0', 'rdfa',  # rare, but I've seen them.
                      'mdata', 'microdata', 'html']:  # wow, there are a lot of RDF formats...
                try:
                    # print "Trying", f
                    g = rdflib.Graph()
                    g.parse(location=i.identifier, format=f, publicID=self.app.NS.local)
                    g.serialize()  # to test that parsing was actually successful.
                    for s, p, o in g:
                        new_np.assertion.add((s, p, o))
                    logging.debug("%s was parsed as %s" % (i.identifier, f))
                    print("%s was parsed as %s" % (i.identifier, f))
                    parsed = True
                    break
                except Exception:
                    print("BF: Could not parse %s as %s" % (i.identifier, f))
                    # traceback.print_exc(file=sys.stdout)
                    pass
            if not parsed:  # probably the best guess anyways, retry to throw the best possible exception.
                print("Could not import ontology %s" % i.identifier)
                return
                # g = rdflib.Graph()
                # g.parse(location=i.identifier, format=file_format, publicID=self.app.NS.local)
                # g.serialize() # to test that parsing was actually successful.

        new_np.pubinfo.add((new_np.assertion.identifier, self.app.NS.prov.wasQuotedFrom, i.identifier))
        new_np.add((new_np.identifier, self.app.NS.sio.isAbout, i.identifier))
