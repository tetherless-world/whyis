# -*- coding:utf-8 -*-
import shutil

from flask_script import Command, Option, Server

import flask
import requests

from whyis import fuseki
import flask


class Fuseki(Command):
    '''Initialize fuseki.'''

    def get_options(self):
        return [
        ]

    def run(self):
        flask.current_app.managed = True

        self.fuseki_port = flask.current_app.config.get('FUSEKI_PORT', 3030)
        print("Starting Fuseki on port",self.fuseki_port)
        self.fuseki_server = fuseki.FusekiServer(port=self.fuseki_port)

        knowledge_endpoint = self.fuseki_server.get_dataset('/knowledge')
        admin_endpoint = self.fuseki_server.get_dataset('/admin')
        self.fuseki_server.process.wait()
