# -*- coding:utf-8 -*-
"""
Flask CLI-based command interface for Whyis.

This module provides Click-based commands for Whyis, replacing the deprecated Flask-Script.
It preserves the subprocess management capabilities needed for embedded Celery, Fuseki, and webpack.
"""

import os
import sys
import json
import signal
import types

# Flask-Script compatibility patches for Flask 3.x
# These must be loaded BEFORE importing any Flask-Script-based commands
# Flask 3.x removed several modules and APIs that Flask-Script depends on

# Patch 1: Create flask._compat module
compat_module = types.ModuleType('flask._compat')
compat_module.text_type = str
compat_module.string_types = (str,)
sys.modules['flask._compat'] = compat_module

# Patch 2: Add _request_ctx_stack if missing (removed in Flask 3.x)
import flask
if not hasattr(flask, '_request_ctx_stack'):
    from werkzeug.local import LocalStack
    flask._request_ctx_stack = LocalStack()

# Patch 3: Add _app_ctx_stack if missing (removed in Flask 3.x)
if not hasattr(flask, '_app_ctx_stack'):
    from werkzeug.local import LocalStack
    flask._app_ctx_stack = LocalStack()

import click
from flask import current_app
from flask.cli import FlaskGroup, with_appcontext

from whyis.app_factory import app_factory
from whyis.config.utils import import_config_module, UnconfiguredAppException
from cookiecutter.main import cookiecutter
from pkg_resources import resource_filename
from re import finditer

# Add current directory to python path to enable imports for app.
try:
    sys.path.index(os.getcwd())
except:
    sys.path.append(os.getcwd())

fuseki_celery_local = False


class CleanChildProcesses:
    """Context manager for subprocess cleanup."""

    def __enter__(self):
        try:
            os.setpgrp()  # create new process group, become its leader
        except PermissionError:
            print('Running in a container, probably.')

    def __exit__(self, type, value, traceback):
        global fuseki_celery_local
        print(fuseki_celery_local)
        if fuseki_celery_local:
            print("Cleaning up local config.")
            if os.path.exists('embedded.conf'):
                os.remove('embedded.conf')
        try:
            os.killpg(0, signal.SIGINT)  # kill all processes in my group
        except KeyboardInterrupt:
            # SIGINT is delivered to this process as well as the child processes.
            # Ignore it so that the existing exception, if any, is returned. This
            # leaves us with a clean exit code if there was no exception.
            pass


def camel_case_split(identifier):
    """Split camelCase or PascalCase string into words."""
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return [m.group(0) for m in matches]


def configure_knowledge_graph():
    """Initialize Whyis configuration using cookiecutter template."""
    try:
        from pip._internal.operations import freeze
    except ImportError:  # pip < 10.0
        from pip.operations import freeze

    # Create project from the cookiecutter-pypackage/ template
    app_dir = os.getcwd()
    dirname = app_dir.split(os.path.sep)[-1]
    project_name = ' '.join(camel_case_split(dirname.replace('_', " ").replace('-', ' '))).title()
    extra_context = {
        'project_name': project_name,
        'project_slug': dirname,
        '__freeze': list(freeze.freeze())
    }
    template_path = resource_filename('whyis', 'config-template')
    os.chdir('..')
    cookiecutter(template_path, extra_context=extra_context,
                 no_input=True, overwrite_if_exists=True)
    os.chdir(app_dir)


def create_app(info=None):
    """Create Flask application instance.
    
    Used by FlaskGroup to create the app for CLI commands.
    """
    global fuseki_celery_local
    
    # Check if we need to configure
    if not os.path.exists('whyis.conf'):
        configure_knowledge_graph()
    
    # Create app using factory
    try:
        config_module = import_config_module()
        app = app_factory(config_module)
    except UnconfiguredAppException:
        # For commands that don't need full config
        from whyis import config_defaults
        app = app_factory(config_defaults)
    
    # Set up embedded services configuration
    if app.config.get('EMBEDDED_CELERY', False) or app.config.get('EMBEDDED_FUSEKI', False):
        fuseki_celery_local = True
        embedded_config = {
            'EMBEDDED_FUSEKI': False,
            'FUSEKI_PORT': app.config['FUSEKI_PORT'],
            'KNOWLEDGE_ENDPOINT': app.config['KNOWLEDGE_ENDPOINT'],
            'ADMIN_ENDPOINT': app.config['ADMIN_ENDPOINT'],
            'EMBEDDED_CELERY': False,
            'CELERY_BROKER_URL': app.config['CELERY_BROKER_URL'],
            'CELERY_RESULT_BACKEND': app.config['CELERY_RESULT_BACKEND']
        }
        with open('embedded.conf', 'w') as embedded_config_file:
            json.dump(embedded_config, embedded_config_file)
    
    return app


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Whyis management commands."""
    pass


# Import command modules
# These will register themselves with the cli group
from whyis.commands import cli as commands_cli

# Register commands from the commands module
# This allows the commands to be imported and registered
try:
    cli.add_command(commands_cli.backup_command)
    cli.add_command(commands_cli.createuser_command)
    cli.add_command(commands_cli.load_command)
    cli.add_command(commands_cli.init_command)
    cli.add_command(commands_cli.sanitize_command)
    cli.add_command(commands_cli.restore_command)
    cli.add_command(commands_cli.retire_command)
    cli.add_command(commands_cli.run_command)
    cli.add_command(commands_cli.test_command)
    cli.add_command(commands_cli.runagent_command)
    cli.add_command(commands_cli.updateuser_command)
except AttributeError:
    # Commands not yet migrated, skip for now
    pass


def main():
    """Main entry point for Whyis CLI."""
    global fuseki_celery_local
    os.environ['FLASK_ENV'] = 'development'
    
    with CleanChildProcesses():
        cli()


if __name__ == "__main__":
    main()
