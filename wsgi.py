# coding:utf-8

import sys
#site.addsitedir('/apps/satoru/venv')
app_dir = '/apps/satoru'
if not app_dir in sys.path:
    sys.path.insert(0, app_dir)

from main import app_factory
import config

application = app_factory(config.Config, config.project_name)
celery = application.celery
