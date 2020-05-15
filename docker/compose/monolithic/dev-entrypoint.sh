#!/bin/bash

python3 manage.py createuser -e whyis@whyis.com -p whyis -u whyis --roles=admin
python3 manage.py runserver -h 0.0.0.0
