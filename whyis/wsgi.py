# coding:utf-8

import sys

from whyis.app_factory import app_factory

application = app_factory()
# Expose celery for celery worker command
# Only set if application has been fully initialized (not in setup_mode)
if not application.setup_mode:
    celery = application.celery
else:
    # In setup mode, create a dummy celery object to prevent import errors
    # when celery worker tries to load 'wsgi.celery'
    from celery import Celery
    celery = Celery('whyis')
