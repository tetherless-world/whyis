import logging
from typing import Dict
import os
from . import default
import json

class UnconfiguredAppException(Exception):
    pass

def import_config_module(app):
    """
    Import and return Flask application configuration, falling back to config_defaults if necessary.
    :return the config module
    """
    app.config.from_object(default.Config)

    try:
        app.config.from_pyfile('whyis.conf')
        app.setup_mode = False
    except FileNotFoundError as e:
        raise UnconfiguredAppException("A knowledge graph is not configured.")

    if os.path.exists('system.conf'):
        print("Loading production config")
        app.config.from_pyfile('system.conf')
    else:
        print("Loading embedded config")
        app.config.from_object(default.EmbeddedSystem)
    if os.path.exists('embedded.conf'):
        print("Loading local embedded config")
        app.config.from_json('embedded.conf')

