#!/bin/bash

WHYIS_IMAGE="${1:-tetherlessworld/whyis:latest}"

mkdir -p test-results/js

echo "`date` Running JavaScript/Vue tests in $WHYIS_IMAGE"
docker run $WHYIS_IMAGE bash -c "cd static && npm test -- --ci --coverage --coverageDirectory=test-results/js/coverage && tar cf test-results-js.tar test-results/js && cat test-results-js.tar" >test-results-js.tar
tar xf test-results-js.tar

echo "`date` JavaScript test results:"
if [ -d "test-results/js/coverage" ]; then
    echo "Coverage report generated successfully"
    if [ -f "test-results/js/coverage/lcov.info" ]; then
        echo "Coverage data:"
        grep -A 2 "end_of_record" test-results/js/coverage/lcov.info | head -20
    fi
else
    echo "Warning: Coverage report not found"
fi

echo "`date` Exiting normally"
exit 0
