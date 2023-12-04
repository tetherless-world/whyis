from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from .service import Service
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


class UpdateChangeService(Service):
    @property
    def query_predicate(self):
        return whyis.updateChangeQuery

    def explain(self, nanopub, i, o):
        Service.explain(self, nanopub, i, o)
        nanopub.pubinfo.add((o.identifier, rdflib.RDF.type, self.getOutputClass()))
        activity = nanopub.provenance.value(nanopub.assertion.identifier, prov.wasGeneratedBy)
        np_assertions = list([i.graph.identifier])
        for assertion in np_assertions:
            nanopub.provenance.add((activity, prov.used, assertion))
            nanopub.provenance.add((nanopub.assertion.identifier, prov.wasDerivedFrom, assertion))
            nanopub.pubinfo.add((nanopub.assertion.identifier, dc.created, rdflib.Literal(datetime.utcnow())))

class TaskPerEntityService(UpdateChangeService):
    pass

class TaskPerNanopubService(UpdateChangeService):
    def process_instances(self, instances, inputGraph):
        self.output_nanopub = self.create_output_nanopub()
        for instance in instances:
            self.process_instance(instance, inputGraph)
        if not self.dry_run:
            flask.current_app.nanopub_manager.publish(self.output_nanopub)
        else:
            print("Not publishing",self.output_nanopub.identifier,", dry run.")
        results = [self.output_nanopub]
        self.output_nanopub.store.close()
        return results

    def process_instance(self, i, inputGraph):
        print("Processing %s %s" % (i.identifier, type(self).__name__) )
        o = self.output_nanopub.assertion.resource(i.identifier)  # OutputClass(i.identifier)
        error = False
        try:
            result = self.process_nanopub(i, o, output_nanopub)
            for new_np in flask.current_app.nanopub_manager.prepare(rdflib.ConjunctiveGraph(store=output_nanopub.store)):
                if len(new_np.assertion) == 0 and not error:
                    continue
                self.explain(new_np, i, o)
                new_np.add((new_np.identifier, sio.isAbout, i.identifier))
                # print new_np.serialize(format="trig")
        except Exception as e:
            output_nanopub.add(
                (output_nanopub.assertion.identifier, flask.current_app.NS.sioc.content, rdflib.Literal(str(e))))
            logging.exception("Error processing resource %s in nanopub %s" % (i.identifier, inputGraph.identifier))
            error = True
