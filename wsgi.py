# coding:utf-8

import sys
app_dir = '/apps/whyis'
if not app_dir in sys.path:
    sys.path.insert(0, app_dir)

from main import app_factory
try:
    import config
except ImportError as e:
    print("WARNING: %s, using defaults file" % str(e))
    import config_defaults as config

application = app_factory(config.Config, config.project_name)
celery = application.celery
