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


class DatasetImporter(UpdateChangeService):
    activity_class = whyis.ImportDatasetEntities

    def getInputClass(self):
        return whyis.DatasetEntity

    def getOutputClass(self):
        return whyis.ImportedDatasetEntity

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
