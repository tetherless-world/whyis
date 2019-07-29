import logging
from typing import Dict


def import_config_module() -> Dict[str, object]:
    """
    Import and return Flask application configuration, falling back to config_defaults if necessary.
    :return the config module
    """
    try:
        import config
    except ImportError as e:
        logging.warning("%s, using config_defaults", str(e))
        import config_defaults as config

    return config
