#!/bin/bash
docker-compose -f db/docker-compose.yml build blazegraph
docker-compose -f app/docker-compose.yml build whyis-ubuntu whyis-server-deps
