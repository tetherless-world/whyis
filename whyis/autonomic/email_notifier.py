from builtins import str
import sadi
import rdflib
import setlr
from datetime import datetime

from .update_change_service import UpdateChangeService
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

from whyis.namespace import *


class EmailNotifier(UpdateChangeService):
    activity_class = whyis.EmailNotification

    def __init__(self, input_type, subject_template, body_template=None, html_template=None,
                 user_predicate=prov.wasAssociatedWith, output_type=whyis.Notified):
        self.body_template = body_template
        self.html_template = html_template
        self.input_type = input_type
        self.output_type = output_type
        self.user_predicate = user_predicate

    def getInputClass(self):
        return self.input_type

    def getOutputClass(self):
        return self.output_type

    def process(self, i, o):
        with flask.current_app.mail.connect() as conn:
            for u in i[self.user_predicate]:
                user = self.datastore.find_user(id=u.identifier)
                parameters = dict(user=user, resource=i)
                args = {
                    'recipients': [user.email],
                    'subject': render_template_string(self.subject_template, user=user, resource=i)
                }
                if self.body_template is not None:
                    args['body'] = render_template_string(self.body_template, user=user, resource=i)
                if self.html_template is not None:
                    args['html'] = render_template_string(self.html_template, user=user, resource=i)
                msg = Message(**args)
                conn.send(msg)
