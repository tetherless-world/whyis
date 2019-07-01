#!/bin/bash

service apache2 start
service jetty9 start
service redis-server start
service celeryd start

if [ ! -f ".data_loaded" ] ;
then
    for i in 1 2 3 4 5; do curl -s http://localhost:8080 &>/dev/null && break || sleep 1; done

    echo "Loading data"
    curl -X POST --data-binary "@admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/admin_namespace.log &&\
    curl -X POST --data-binary "@knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace > /data/knowledge_namespace.log
    echo "Loaded data"

    echo "`date +%Y-%m-%dT%H:%M:%S%:z`" > .data_loaded
fi


echo "\n\
Please configure Whyis at /apps/whyis/config.py to ensure correct customization.\n\
Follow the instructions for 'Configure Whyis' at http://tetherless-world.github.io/whyis/install.\n\
\n\
To run whyis in development mode, run the following to start it:\n\
\n\
 > sudo su - whyis\n\
 > cd /apps/whyis\n\
 > source venv/bin/activate\n\
 > python manage.py runserver\n\
\n"

exec "$@"
