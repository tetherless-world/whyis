# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask
from pathlib import Path
import os
import csv
from depot.manager import DepotManager
import tempfile

import rdflib

import shutil

class Sanitize(Command):
    '''Sanitizes a whyis KG for import.'''

    def get_options(self):
        return [
            Option ('-i', '--input', dest='input_directory', help='Input backup path', required=True, type=str),
            Option ('-o', '--output', dest='output_directory', help='Outout backup path', required=True, type=str),
        ]

    def run(self, input_directory, output_directory):
        app = flask.current_app
        from pydoc import locate

        # copy everything over, then we will rewrite as needed.
        print("Copying backup...")
        shutil.copytree(input_directory, output_directory)

        print("Fixing files...")
        files = ['nanopub_index']
        print('Loading files list...')
        with open(os.path.join(input_directory, 'nanopub_index')) as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            files = files + ['nanopublications/%s/file' % x[1] for x in reader]
        for file_name in files:
            print(file_name)
            if file_name.endswith('file') or file_name.endswith('nanopub_index'):
                # construct full file path
                source = os.path.join(input_directory, file_name)
                destination = os.path.join(output_directory, file_name)
                with open(source) as source_file:
                    data = source_file.read()
                    changed = False
                    # Fix URN-based URIs to be local.
                    if 'urn:' in data:
                        print('Fixing', file_name)
                        data = data.replace('urn:', app.config['LOD_PREFIX']+'/node/')
                        changed = True
                    if file_name.endswith('file'):
                        graph_changed = False
                        g = rdflib.ConjunctiveGraph()
                        g.parse(data=data, format="nquads")

                        # Remove invalid literals.
                        # Fuseki has an especially hard time with them.
                        for s,p,o,c in g.quads():
                            if isinstance(o, rdflib.Literal) and o.value is None:
                                print("Removing",(s,p,o,c))
                                graph_changed = True
                                g.remove((s,p,o,c))
                        if graph_changed:
                            changed = True
                            data = g.serialize(format="trig")
                    if changed:
                        with open(destination, 'w') as destination_file:
                            destination_file.write(data)
        print("Complete.")
