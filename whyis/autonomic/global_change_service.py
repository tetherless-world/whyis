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

from whyis.namespace import whyis


class GlobalChangeService(Service):
    @property
    def query_predicate(self):
        return whyis.globalChangeQuery
