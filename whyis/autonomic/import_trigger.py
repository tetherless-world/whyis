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


class ImportTrigger(UpdateChangeService):
    __doc__ = '''
Run the relevant on-demand importer when an entity covered by that importer
is mentioned in a nanopublication. Customize the set of entities to import by
passing in a `query` parameter to the constructor, which will be used to detect
the entities to import.

CAUTION: By default, the agent will follow all entities that are mentioned in
the graph. If the import itself mentions another entity covered by an importer,
that process will continue until no more entities are discovered. For very large
knowledge graphs, this can be many HTTP transactions and may cause issues with
your API license. A larger batch import may be the better choice in this case.
    '''
    activity_class = whyis.ImportEntities

    def __init(self, query):
        if query is None:
            prefixes = [x.detect_url for x in self.app.config['namespaces']]
            self._query = '''select distinct ?resource where {
  ?resource a ?type.
  FILTER (regex(str(?resource), "^(%s)")) .
} ''' % '|'.join(prefixes)

    def getInputClass(self):
        return whyis.Entity

    def getOutputClass(self):
        return whyis.ImportedEntity

    _query = None

    def get_query(self):
        if self._query is None:
            prefixes = [x.detect_url for x in self.app.config['namespaces']]
            self._query = '''select distinct ?resource where {
  ?resource void:inDataset ?dataset.
  FILTER (regex(str(?resource), "^(%s)")) .
  filter not exists {
    ?assertion prov:wasQuotedFrom ?resource.
  }
} ''' % '|'.join(prefixes)
            print(self._query)

        return self._query

    def process(self, i, o):
        node = self.app.run_importer(i.identifier)
