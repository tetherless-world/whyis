#!/bin/bash

WHYIS_IMAGE="${1:-tetherlessworld/whyis:latest}"

mkdir -p test-results/py

# docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test"
# docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test --ci && cat test-results/py/results.xml"

echo "`date` Running Python tests in $WHYIS_IMAGE"
docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "mkdir -p test-results/py && python3 manage.py test --ci >test-results/py/test.out 2>test-results/py/test.err; tar cf test-results-py.tar test-results/py && cat test-results-py.tar" >test-results-py.tar
tar xf test-results-py.tar
echo "`date` Python test stdout:"
cat test-results/py/test.out
echo "`date` Python test stderr:"
cat test-results/py/test.err
if [ ! -f "test-results/py/results.xml" ]; then
    echo "Python test results.xml does not exist, exiting abnormally"
    exit 1
fi
if [ "$(grep -c 'failure ' test-results/py/results.xml)" -ge 1 ]; then
    echo "Python test results.xml has failures, exiting abnormally"
    exit 1
fi

echo "`date` Exiting normally"
exit 0
