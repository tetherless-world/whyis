#!/bin/bash
WHYIS_IMAGE_TAG=latest docker-compose build whyis-deps
WHYIS_IMAGE_TAG=master docker-compose build whyis-deps
