# -*- coding:utf-8 -*-
import shutil

from flask_script import Command, Option, Server

import flask

import rdflib
from nanopub import Nanopublication
import tempfile

from whyis.namespace import np


class LoadNanopub(Command):
    '''Add a nanopublication to the knowledge graph.'''

    _TEMP_STORE_DEFAULT = "Sleepycat"

    def get_options(self):
        return [
            Option('-i', '--input', dest='input_file', required=True, help='Path to file containing nanopub', type=str),
            Option('-f', '--format', dest='file_format', default='trig', help='File format (default: trig; also xml, n3, nt, trix, rdfa)', type=str),
            Option('-r', '--revises', dest='was_revision_of', type=str),
            Option("--temp-store", dest="temp_store", type=str, default=self._TEMP_STORE_DEFAULT, help="backing store type to use for temporary graphs")
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
        g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize(), store=temp_store)
        if temp_store == "Sleepycat":
            g_store_tempdir = tempfile.mkdtemp()
            g.store.open(g_store_tempdir, True)
        else:
            g_store_tempdir = None
        # g = rdflib.ConjunctiveGraph(identifier=rdflib.BNode().skolemize())

        try:
            g1 = g.parse(location=input_file, format=file_format, publicID=flask.current_app.NS.local)
            if len(list(g.subjects(rdflib.RDF.type, np.Nanopublication))) == 0:
                print("Could not find existing nanopublications.", len(g1), len(g))
                new_np = Nanopublication(store=g1.store)
                new_np.add((new_np.identifier, rdflib.RDF.type, np.Nanopublication))
                new_np.add((new_np.identifier, np.hasAssertion, g1.identifier))
                new_np.add((g1.identifier, rdflib.RDF.type, np.Assertion))

            nanopub_prepare_graph = rdflib.ConjunctiveGraph(store=temp_store)
            if temp_store == "Sleepycat":
                nanopub_prepare_graph_store_tempdir = tempfile.mkdtemp()
                nanopub_prepare_graph.store.open(nanopub_prepare_graph_store_tempdir, True)
            else:
                nanopub_prepare_graph_store_tempdir = None

            try:
                nanopubs = []
                for npub in flask.current_app.nanopub_manager.prepare(g, store=nanopub_prepare_graph.store):
                    if was_revision_of is not None:
                        for r in was_revision_of:
                            print("Marking as revision of", r)
                            npub.pubinfo.add((npub.assertion.identifier, flask.current_app.NS.prov.wasRevisionOf, r))
                    print('Prepared', npub.identifier)
                    nanopubs.append(npub)
                flask.current_app.nanopub_manager.publish(*nanopubs)
                print("Published", npub.identifier)
            finally:
                if nanopub_prepare_graph_store_tempdir is not None:
                    shutil.rmtree(nanopub_prepare_graph_store_tempdir)
        finally:
            if g_store_tempdir is not None:
                shutil.rmtree(g_store_tempdir)
