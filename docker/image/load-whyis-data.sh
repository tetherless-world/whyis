#!/bin/bash

if [ ! -f "/data/.whyis_data_loaded" ] ;
then
    for i in 1 2 3 4 5; do curl -s http://localhost:8080 &>/dev/null && break || sleep 1; done

    curl -s -X POST --data-binary "@/apps/whyis/admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log
    curl -s -X POST --data-binary "@/apps/whyis/knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > /data/.whyis_data_loaded
fi
