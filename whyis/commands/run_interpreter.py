# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask
from whyis import interpreter


class RunInterpreter(Command):
    '''Add a nanopublication to the knowledge graph.'''

    def get_options(self):
        return [
            Option('--input', '-i', dest='config_file',
                   type=str),
        ]

    def run(self, config_file=None):
        app = flask.current_app
        if config_file is not None:
            agent = interpreter.Interpreter(config_fn=config_file)
            agent.app = app
            agent.process_graph(app.db)
