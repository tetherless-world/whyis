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
