# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask


class RetireNanopub(Command):
    '''Retire a nanopublication from the knowledge graph.'''

    def get_options(self):
        return [
            Option('--nanopub_uri', '-n', dest='nanopub_uri',
                   type=str),
        ]

    def run(self, nanopub_uri):
        flask.current_app.nanopub_manager.retire(nanopub_uri)
