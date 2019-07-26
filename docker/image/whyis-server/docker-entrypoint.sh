#!/bin/bash

# jetty9 service start returns 1, even though Jetty has started successfully.
# set -e

for i in 1 2 3 4 5; do curl -s http://blazegraph:8080 &>/dev/null && break || sleep 1; done

socat TCP4-LISTEN:6379,fork,reuseaddr TCP4:redis:6379 &
socat TCP4-LISTEN:8080,fork,reuseaddr TCP4:blazegraph:8080 &

service apache2 start 1>&2
service celeryd start 1>&2

if [ ! -f "/data/.whyis_data_loaded" ] ;
then
    curl -s -X POST --data-binary "@/apps/whyis/admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log
    curl -s -X POST --data-binary "@/apps/whyis/knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > /data/.whyis_data_loaded
fi

exec "$@"
