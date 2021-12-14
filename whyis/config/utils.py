import logging
from typing import Dict
import os
from . import default

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
        raise UnconfiguredAppException("A knowleedge graph is not configured.")

    if os.path.exists('system.conf'):
        app.config.from_pyfile('system.conf')
    else:
        app.config.from_object(default.EmbeddedSystem)
