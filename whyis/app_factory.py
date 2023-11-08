from whyis.config.utils import import_config_module
from flask_pluginengine import PluginEngine
import os
import sys

_app = None

def app_factory(blueprints=None):
    global _app
    if _app is None:
        from whyis.app import App, PROJECT_PATH
        # you can use Empty directly if you wish
        _app = App("Whyis", root_path=PROJECT_PATH,
                           instance_relative_config=True,
                           instance_path=os.getcwd())
        #print dir(config)
        import_config_module(_app)
        _app.plugin_engine = PluginEngine(_app)
        _app.plugin_engine.load_plugins(_app)

        if blueprints:
            _app.add_blueprint_list(blueprints)
        if not _app.setup_mode:
            _app.setup()

    return _app
