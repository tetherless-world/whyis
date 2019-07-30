# -*- coding:utf-8 -*-

from flask_script import Command

from base64 import b64encode
import os
from cookiecutter.main import cookiecutter


class Configure(Command):
    '''Create a Whyis configuration and customization directory.'''

    def get_options(self):
        return [
        ]

    def run(self, extension_directory=None, extension_name=None):
        def rando():
            return b64encode(os.urandom(24)).decode('utf-8')

        # Create project from the cookiecutter-pypackage/ template
        extra_context = {'SECRET_KEY': rando(), 'SECURITY_PASSWORD_SALT': rando()}
        cookiecutter('config-template/', extra_context=extra_context)
