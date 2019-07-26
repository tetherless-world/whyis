#!/bin/bash

WHYIS_IMAGE="${1:-tetherlessworld/whyis:latest}"

mkdir -p test-results/py

# docker run $WHYIS_IMAGE bash -c "python3 manage.py test"
docker run $WHYIS_IMAGE bash -c "python3 manage.py test --ci && cat test-results/py/results.xml"

#docker run $WHYIS_IMAGE bash -c "python3 manage.py test --ci &>/dev/null && tar cf test-results-py.tar test-results/py && cat test-results-py.tar" >test-results-py.tar
#
#tar xf test-results-py.tar
#
#if [ ! -f "test-results/py/results.xml" ]; then
#    exit 1
#fi
#
#cat test-results/py/results.xml
#
#if [ "$(grep -c "failure "test-results/py/results.xml)" -ge 1 ]; then
#    exit 1
#else
#    exit 0
#fi
