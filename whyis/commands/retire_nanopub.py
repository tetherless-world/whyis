# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask


class RetireNanopub(Command):
    '''Retire a nanopublication from the knowledge graph.'''

    def get_options(self):
        return [
            Option('-n', '--nanopub_uri', dest='nanopub_uri', required=True, help='URI of the nanopub to retire', type=str),
        ]

    def run(self, nanopub_uri):
        flask.current_app.nanopub_manager.retire(nanopub_uri)
