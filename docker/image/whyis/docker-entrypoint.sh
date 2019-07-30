#!/bin/bash

# jetty9 service start returns 1, even though Jetty has started successfully.
# set -e

service apache2 start 1>&2
service jetty9 start 1>&2
service redis-server start 1>&2
service celeryd start 1>&2

/load-whyis-data.sh

exec "$@"
