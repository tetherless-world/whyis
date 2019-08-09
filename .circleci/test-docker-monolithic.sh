#!/bin/bash

WHYIS_IMAGE="${1:-tetherlessworld/whyis:latest}"

mkdir -p test-results/py

echo "Running Python tests in $WHYIS_IMAGE, will print to console"
docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test"

# docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test --ci && cat test-results/py/results.xml"

echo "Running Python tests in $WHYIS_IMAGE, will output junit.xml and coverage reports"
docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test --ci &>/dev/null && tar cf test-results-py.tar test-results/py && cat test-results-py.tar" >test-results-py.tar

tar xf test-results-py.tar

if [ ! -f "test-results/py/results.xml" ]; then
    echo "Python test results.xml does not exist, exiting abnormally"
    exit 1
fi

echo "Python test results.xml:"
cat test-results/py/results.xml

if [ "$(grep -c 'failure ' test-results/py/results.xml)" -ge 1 ]; then
    echo "Python test results.xml has failures, exiting abnormally"
    exit 1
fi

mkdir -p test-results/js

echo "Running integration tests in $WHYIS_IMAGE, will write junit.xml"
docker run $WHYIS_IMAGE bash -c "curl -sL https://deb.nodesource.com/setup_12.x | bash - && apt-get install -y nodejs xvfb libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 && mkdir -p test-results/js && cd tests/integration && npm install && CYPRESS_baseUrl=http://localhost npm run cypress:run"
# docker run $WHYIS_IMAGE bash -c "curl -sL https://deb.nodesource.com/setup_12.x | bash - && apt-get install -y nodejs xvfb libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 && mkdir -p test-results/js && cd tests/integration && npm install && CYPRESS_baseUrl=http://localhost npm run cypress:run-ci &>/dev/null && cat /apps/whyis/test-results/js/results.xml" >test-results/js/results.xml

if [ "$(grep -c 'failure ' test-results/js/results.xml)" -ge 1 ]; then
    echo "Integration test results.xml has failures, exiting abnormally"
    exit 1
fi

echo "Exiting normally"
exit 0
