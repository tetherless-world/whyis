# -*- coding:utf-8 -*-

from flask_script import Command

from base64 import b64encode
import os
from cookiecutter.main import cookiecutter
from pkg_resources import resource_filename, resource_listdir

try:
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze

class Configure(Command):
    '''Create a Whyis configuration and customization directory, using input parameters from stdin'''

    def get_options(self):
        return [
        ]

    def run(self, extension_directory=None, extension_name=None):
        def rando():
            return b64encode(os.urandom(24)).decode('utf-8')

        # Create project from the cookiecutter-pypackage/ template
        extra_context = {
            '__freeze' : list(freeze.freeze())
        }
        template_path = resource_filename('whyis', 'config-template')

        cookiecutter(template_path, extra_context=extra_context)
