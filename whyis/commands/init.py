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

class Initialize(Command):
    '''Initialize fuseki.'''

    def get_options(self):
        return [
        ]

    def run(self):
        pass
