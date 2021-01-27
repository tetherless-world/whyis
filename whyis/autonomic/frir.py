from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime
from depot.manager import DepotManager

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

import hashlib
from uuid import uuid4

from rdflib import compare

pexp = rdflib.Namespace('tag:tw.rpi.edu,2011:expression_rgda1-sha256-')
pmanif = rdflib.Namespace('tag:tw.rpi.edu,2011:manifestation_sha256-')
nfo = rdflib.Namespace('http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#')


def rgda1_digest(graph):
    g = rdflib.Graph()
    g += graph
    ig = compare.to_isomorphic(g)
    return ig.graph_digest()

def uuid(graph):
    return int(uuid4())

def sha256(f):
    h = hashlib.sha256()
    for chunk in iter(lambda: f.read(4096), b""):
        h.update(chunk)
    hd = h.hexdigest()
    result = int(hd, 16)
    return result

class FRIRArchiver(UpdateChangeService):
    activity_class = whyis.Archive

    def __init__(self, expression_digest=rgda1_digest, manifestation_digest=sha256):
        self.expression_digest = expression_digest
        self.manifestation_digest = manifestation_digest

    def getInputClass(self):
        return np.Nanopublication

    def getOutputClass(self):
        return whyis.ArchivedNanopublication

    def get_query(self):
        return '''
prefix setl: <http://purl.org/twc/vocab/setl/>
select distinct ?resource where {
  ?resource a np:Nanopublication.
  filter not exists {
    ?resource a whyis:FRIRNanopublication.
  }
  filter not exists {
    ?resource a whyis:ArchivedNanopublication.
  }
}'''

    def process_nanopub(self, i, o, new_np):
        assertion = i.graph
        nanopub = Nanopublication(i.graph.store, i.identifier)
        quads = nanopub.serialize(format="nquads")
        i.identifier.split('/')[-1]
        fileid = self.app.nanopub_depot.create(quads, i.identifier.split('/')[-1]+'.nq', "application/n-quads")
        o.add(rdflib.RDF.type, whyis.ArchivedNanopublication)
        new_np.pubinfo.add((new_np.identifier, rdflib.RDF.type, whyis.FRIRNanopublication))
        expressions = dict([(part.identifier, self.expression_digest(part))
                            for part in [nanopub.assertion, nanopub.provenance, nanopub.pubinfo]])
        expressions[nanopub.identifier] = sum(expressions.values())
        nanopub_expression_uri = pexp[hex(expressions[nanopub.identifier])[2:]]
        for work, expression in expressions.items():
            exp = pexp[hex(expression)[2:]]
            o.graph.add((work, frbr.realization, exp))
            o.graph.add((work, rdflib.RDF.type, frbr.Work))
            o.graph.add((exp, rdflib.RDF.type, frbr.Expression))

        with self.app.nanopub_depot.get(fileid) as stored_file:
            manifestation_id = self.manifestation_digest(stored_file)
        manifestation = pmanif[hex(manifestation_id)[2:]]
        o.graph.add((nanopub_expression_uri, frbr.embodiment, manifestation))

        o.graph.add((manifestation, rdflib.RDF.type, pv.File))
        o.graph.add((manifestation, whyis.hasFileID, rdflib.Literal(fileid)))
        o.graph.add((manifestation, dc.created, rdflib.Literal(datetime.utcnow())))
        o.graph.add((manifestation, NS.ov.hasContentType, rdflib.Literal("application/n-quads")))
        o.graph.add((manifestation, rdflib.RDF.type, NS.mediaTypes["application/n-quads"]))
        o.graph.add((NS.mediaTypes["application/n-quads"], rdflib.RDF.type, dc.FileFormat))
