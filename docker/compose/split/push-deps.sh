#!/bin/bash
docker-compose -f db/docker-compose.yml push blazegraph
docker-compose -f app/docker-compose.yml push whyis-ubuntu whyis-server-deps
