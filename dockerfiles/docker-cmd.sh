#!/bin/bash

# service jetty9 stop
# rm -f /var/run/jetty9.pid
service jetty9 start

if [ ! -f ".data_loaded" ] ;
then
    for i in 1 2 3 4 5; do curl -s http://localhost:8080 &>/dev/null && break || sleep 1; done

    echo "Loading data"
    curl -X POST --data-binary "@admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log &&\
	curl -X POST --data-binary "@knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log
	echo "Loaded data"

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > .data_loaded
fi

/bin/bash