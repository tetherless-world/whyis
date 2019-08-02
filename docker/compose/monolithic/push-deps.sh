#!/bin/bash
WHYIS_IMAGE_TAG=latest docker-compose push whyis-deps
WHYIS_IMAGE_TAG=master docker-compose push whyis-deps
