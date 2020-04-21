#!/bin/bash
CYPRESS_baseUrl=http://whyis

curl --retry 5 --retry-connrefused "$CYPRESS_baseUrl" > /dev/null
cypress run --spec cypress/integration/whyis/**/*
tar cf test-results-js.tar results
