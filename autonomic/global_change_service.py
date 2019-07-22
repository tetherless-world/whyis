from __future__ import print_function
from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from autonomic.service import Service
from nanopub import Nanopublication
from datastore import create_id
import flask
from flask import render_template
from flask import render_template_string
import logging

import sys, traceback

import database

import tempfile

from depot.io.interfaces import StoredFile

from .namespaces import whyis


class GlobalChangeService(Service):
    @property
    def query_predicate(self):
        return whyis.globalChangeQuery
