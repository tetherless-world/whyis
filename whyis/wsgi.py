# coding:utf-8

import sys

from whyis.app_factory import app_factory

application = app_factory()
if not application.setup_mode:
    celery = application.celery
