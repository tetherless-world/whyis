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


class LoadNanopub(Command):
    '''Add a nanopublication to the knowledge graph.'''

    _TEMP_STORE_DEFAULT = "Sleepycat"

    def get_options(self):
        return [
            Option('-w', '--whyis', dest='whyis_instance', required=True, help='URL for Whyis instance', type=str, default='http://localhost'),
            Option('-i', '--input', dest='input_file', required=True, help='Path to file containing nanopub', type=str),
            Option('-f', '--format', dest='file_format', default='trig', help='File format (default: trig; also turtle, json-ld, xml, nquads, nt, rdfa)', type=str),
            Option('-u', '--user', dest='username', required=False, help='User to upload as', type=str),
            Option('-p', '--password', dest='password', required=False, help='Password to authenticate user', type=str),
        ]

    def run(self, whyis_instance, input_file, file_format, username=None, password=None):
        content_type = DATA_EXTENSIONS.get(file_format, file_format)

        with open(input_file, 'rb') as input:
            request = {
                'url' : '%s/pub' % whyis_instance,
                'data' : input,
                'headers' : { 'Content-Type' : content_type},
            }
            if username is not None:
                request['auth'] = (username, password)
            response = requests.post(**request)
            if 'Location' in response.headers:
                print('Created nanopublication:', response.headers)
            if response.status_code != 201:
                sys.exit(response.text)
