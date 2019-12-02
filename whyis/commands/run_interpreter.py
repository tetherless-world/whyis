# -*- coding:utf-8 -*-

from flask_script import Command, Option

import flask
from whyis import interpreter


class RunInterpreter(Command):
    '''Deprecated'''

    def get_options(self):
        return [
            Option('--input', '-i', dest='config_file', required=True,
                   type=str),
        ]

    def run(self, config_file):
        app = flask.current_app
        agent = interpreter.Interpreter(config_fn=config_file)
        agent.app = app
        agent.process_graph(app.db)
