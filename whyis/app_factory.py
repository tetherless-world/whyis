from whyis.config.utils import import_config_module
import os
import sys
from whyis.config import default

_app = None

def app_factory(config=default.Config, blueprints=None):
    global _app
    if _app is None:
        from whyis.app import App, PROJECT_PATH
        # you can use Empty directly if you wish
        _app = App("Whyis", root_path=PROJECT_PATH,
                           instance_relative_config=True,
                           instance_path=os.getcwd())
        #print dir(config)
        import_config_module(_app, config)
        if blueprints:
            _app.add_blueprint_list(blueprints)
        _app.setup()

    return _app
