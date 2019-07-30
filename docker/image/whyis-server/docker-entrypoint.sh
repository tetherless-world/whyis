#!/bin/bash

# jetty9 service start returns 1, even though Jetty has started successfully.
# set -e

for i in 1 2 3 4 5; do curl -s http://blazegraph:8080 &>/dev/null && break || sleep 1; done

socat TCP4-LISTEN:6379,fork,reuseaddr TCP4:redis:6379 &
socat TCP4-LISTEN:8080,fork,reuseaddr TCP4:blazegraph:8080 &

service apache2 start 1>&2
service celeryd start 1>&2

/load-whyis-data.sh

exec "$@"
