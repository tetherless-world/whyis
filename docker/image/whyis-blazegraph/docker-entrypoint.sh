#!/bin/sh
echo "Deleting existing jetty.start to get around a bug"
rm -f /var/lib/jetty/jetty.start
echo "Delegating to Jetty entrypoint"
/jetty-docker-entrypoint.sh $*
