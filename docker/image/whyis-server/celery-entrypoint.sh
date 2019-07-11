#!/bin/bash

socat TCP4-LISTEN:6379,fork,reuseaddr TCP4:redis:6379

celery worker --logfile /var/log/celery/%n.log --concurrency=8 -A wsgi.celery
