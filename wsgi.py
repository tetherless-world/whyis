# coding:utf-8

import sys
app_dir = '/apps/whyis'
if not app_dir in sys.path:
    sys.path.insert(0, app_dir)

from main import app_factory

from whyis.config_utils import import_config_module
config = import_config_module()

application = app_factory(config.Config, config.project_name)
celery = application.celery
