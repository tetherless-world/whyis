# coding:utf-8

import sys

from whyis.app_factory import app_factory

from whyis.config_utils import import_config_module
config = import_config_module()

application = app_factory(config.Config, config.project_name)
celery = application.celery
