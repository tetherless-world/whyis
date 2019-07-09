#!/bin/bash

# jetty9 service start returns 1, even though Jetty has started successfully.
# set -e

service apache2 start 1>&2
service jetty9 start 1>&2
service redis-server start 1>&2
service celeryd start 1>&2

if [ ! -f "/data/.whyis_data_loaded" ] ;
then
    for i in 1 2 3 4 5; do curl -s http://localhost:8080 1>&2 && break || sleep 1; done

    curl -s -X POST --data-binary "@admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log
    curl -s -X POST --data-binary "@knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > /data/.whyis_data_loaded
fi

exec "$@"
