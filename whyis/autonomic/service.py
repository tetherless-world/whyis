from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime
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


class Service(sadi.Service):
    dry_run = False

    activity_class = whyis.Agent

    def get_query(self):
        return '''select ?resource where {
    ?resource rdf:type/rdfs:subClassOf* %s.
    filter not exists { ?resource rdf:type/rdfs:subClassOf* %s. }
}''' % (self.getInputClass().n3(), self.getOutputClass().n3())

    def annotateServiceDescription(self, desc):
        desc.add(self.query_predicate, rdflib.Literal(self.get_query()))

    def processGraph(self, content, type):
        inputGraph = sadi.SADIGraph()
        self.deserialize(inputGraph, content, type)
        return process

    def explain(self, nanopub, i, o):
        activity = nanopub.provenance.resource(rdflib.BNode())
        activity.add(rdflib.RDF.type, self.activity_class)
        nanopub.pubinfo.add((o.identifier, rdflib.RDF.type, self.getOutputClass()))
        nanopub.provenance.add((nanopub.assertion.identifier, prov.wasGeneratedBy, activity.identifier))

    def getInstances(self, graph):
        if hasattr(graph.store, "nsBindings"):
            graph.store.nsBindings = {}
        prefixes = self.app.NS.prefixes
        if hasattr(self, 'prefixes'):
            prefixes = self.prefixes
        return [graph.resource(i) for i, in graph.query(self.get_query(), initNs=prefixes)]

    def process_graph(self, inputGraph):
        instances = self.getInstances(inputGraph)
        results = []
        for i in instances:
            print("Processing", i.identifier, self)
            output_nanopub = self.app.nanopub_manager.new()
            o = output_nanopub.assertion.resource(i.identifier)  # OutputClass(i.identifier)
            error = False
            try:
                result = self.process_nanopub(i, o, output_nanopub)
            except Exception as e:
                output_nanopub.add(
                    (output_nanopub.assertion.identifier, self.app.NS.sioc.content, rdflib.Literal(str(e))))
                logging.exception("Error processing resource %s in nanopub %s" % (i.identifier, inputGraph.identifier))
                error = True
            for new_np in self.app.nanopub_manager.prepare(rdflib.ConjunctiveGraph(store=output_nanopub.store)):
                if len(new_np.assertion) == 0 and not error:
                    continue
                self.explain(new_np, i, o)
                new_np.add((new_np.identifier, sio.isAbout, i.identifier))
                # print new_np.serialize(format="trig")
                if not self.dry_run:
                    self.app.nanopub_manager.publish(new_np)
                else:
                    print("Not publishing",new_np.identifier,", dry run.")
                results.append(new_np)
        return results

    def process_nanopub(self, i, o, output_nanopub):
        self.process(i, o)
