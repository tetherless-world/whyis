#!/bin/bash

# jetty9 service start returns 1, even though Jetty has started successfully.
# set -e

socat TCP4-LISTEN:6379,fork,reuseaddr TCP4:redis:6379 
socat TCP4-LISTEN:8080,fork,reuseaddr TCP4:blazegraph:8080

service apache2 start 1>&2

if [ ! -f "/data/.whyis_data_loaded" ] ;
then
    curl -s --retry 5 http://localhost:8080 &>/dev/null

    curl -s -X POST --data-binary "@admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log
    curl -s -X POST --data-binary "@knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > /data/.whyis_data_loaded
fi

exec "$@"
