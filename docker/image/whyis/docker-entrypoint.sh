#!/bin/bash

service apache2 start &>>/docker-entrypoint.log
service jetty9 start &>>/docker-entrypoint.log
service redis-server start &>/docker-entrypoint.log
service celeryd start &>/docker-entrypoint.log

if [ ! -f ".data_loaded" ] ;
then
    for i in 1 2 3 4 5; do curl -s http://localhost:8080 &>/dev/null && break || sleep 1; done

    curl -s -X POST --data-binary "@admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log 2>>/docker-entrypoint.log &&\
    curl -s -X POST --data-binary "@knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log 2>>/docker-entrypoint.log

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > .data_loaded
fi

exec "$@"
