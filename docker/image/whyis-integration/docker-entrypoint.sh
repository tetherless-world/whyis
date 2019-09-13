#!/bin/bash
CYPRESS_baseUrl=http://whyis

curl --retry 5 --retry-connrefused http://whyis > /dev/null
cypress run --spec cypress/integration/whyis/**/*
tar cf test-results-js.tar results
