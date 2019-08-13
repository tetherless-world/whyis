#!/bin/bash

if [ ! -f "/data/.whyis_data_loaded" ] || [ ! -z "${LOAD_WHYIS_DATA_FORCE}" ]; then
  for i in 1 2 3 4 5; do curl -s http://localhost:8080 &>/dev/null && break || sleep 1; done

  curl -s -X POST --data-binary "@/apps/whyis/admin.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace &>>/data/.load_whyis_data.out
  curl -s -X POST --data-binary "@/apps/whyis/knowledge.properties" -H 'Content-Type:text/plain' http://localhost:8080/blazegraph/namespace &>>/data/.load_whyis_data.out

  echo "$(date +%Y-%m-%dT%H:%M:%S%:z)" >/data/.whyis_data_loaded
fi

APPNAME=$(find /apps -maxdepth 1 -type d -and -not -path /apps/whyis -and -not -path /apps -and -not -path '*/\.*' -exec basename \{} \;)

if [ -f "/apps/${APPNAME}/load-data.sh" ]; then
  if [ ! -f "/data/.${APPNAME}_data_loaded" ] || [ ! -z "${LOAD_WHYIS_DATA_FORCE}" ]; then
    sudo -i -u whyis /apps/${APPNAME}/load-data.sh >"/data/.${APPNAME}_load_data.out" 2>"/data/.${APPNAME}_load_data.err"
    echo "$(date +%Y-%m-%dT%H:%M:%S%:z)" >"/data/.${APPNAME}_data_loaded"
  fi
fi
