# -*- coding:utf-8 -*-
import shutil

from flask_script import Command, Option, Server

import flask
import requests

from whyis.data_extensions import DATA_EXTENSIONS

import rdflib
from whyis.nanopub import Nanopublication
import tempfile

from whyis.namespace import np
from whyis.blueprint.nanopub.nanopub_utils import load_nanopub_graph
import sys

class LoadNanopub(Command):
    '''Add a nanopublication to the knowledge graph.'''

    _TEMP_STORE_DEFAULT = None

    def get_options(self):
        return [
            Option('-i', '--input', dest='input_file', required=True, help='Path to file containing nanopub', type=str),
            Option('-f', '--format', dest='file_format', default='trig', help='File format (default: trig; also turtle, json-ld, xml, nquads, nt, rdfa)', type=str),
            Option('-r', '--revises', dest='was_revision_of', help="URI of nanopublication that this is a revision of", type=str),
            Option("--temp-store", dest="temp_store", type=str, default=self._TEMP_STORE_DEFAULT, help="backing store type to use for temporary graphs; deprecated")
        ]

    def run(self, input_file, file_format, temp_store=_TEMP_STORE_DEFAULT, was_revision_of=None):
        flask.current_app.managed = True
        if was_revision_of is not None:
            wasRevisionOf = set(flask.current_app.db.objects(predicate=np.hasAssertion,
                                                             subject=rdflib.URIRef(was_revision_of)))
            if len(wasRevisionOf) == 0:
                print("Could not find active nanopublication to revise:", was_revision_of)
                return
            was_revision_of = wasRevisionOf
        g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize())
        if temp_store == "Oxigraph":
            g_store_tempdir = tempfile.mkdtemp()
            g.store.open(g_store_tempdir, True)
        else:
            g_store_tempdir = None
        # g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize())

        try:
            g1 = load_nanopub_graph(location=input_file, format=file_format, store=g.store)

            nanopubs = []
            for npub in flask.current_app.nanopub_manager.prepare(g):
                if was_revision_of is not None:
                    for r in was_revision_of:
                        print("Marking as revision of", r)
                        npub.pubinfo.add((npub.assertion.identifier, flask.current_app.NS.prov.wasRevisionOf, r))
                print('Prepared', npub.identifier)
                nanopubs.append(npub)
            flask.current_app.nanopub_manager.publish(*nanopubs)
            print("Published", npub.identifier)
        finally:
            if g_store_tempdir is not None:
                shutil.rmtree(g_store_tempdir)
