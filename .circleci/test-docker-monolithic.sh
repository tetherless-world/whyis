#!/bin/bash

WHYIS_IMAGE="${1:-tetherlessworld/whyis:latest}"
WHYIS_DEMO_IMAGE="${1:-tetherlessworld/whyis-demo:latest}"

mkdir -p test-results/py

# docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test"
# docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "python3 manage.py test --ci && cat test-results/py/results.xml"

echo "Running Python tests in $WHYIS_IMAGE"
docker run -e "CI=$CI" $WHYIS_IMAGE bash -c "mkdir -p test-results/py && python3 manage.py test --ci >test-results/py/test.out 2>test-results/py/test.err; tar cf test-results-py.tar test-results/py && cat test-results-py.tar" >test-results-py.tar
tar xf test-results-py.tar
cat test-results/py/test.out
if [ ! -f "test-results/py/results.xml" ]; then
    echo "Python test results.xml does not exist, exiting abnormally"
    exit 1
fi
if [ "$(grep -c 'failure ' test-results/py/results.xml)" -ge 1 ]; then
    echo "Python test results.xml has failures, exiting abnormally"
    exit 1
fi

mkdir -p test-results/js
echo "Running integration tests in $WHYIS_DEMO_IMAGE"
#JS_REDIRECT=""
#docker run $WHYIS_DEMO_IMAGE bash -c "mkdir -p test-results/js && curl -sL https://deb.nodesource.com/setup_12.x | bash - $JS_REDIRECT && apt-get install -y nodejs xvfb libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 $JS_REDIRECT && cd tests/integration && npm install $JS_REDIRECT && CYPRESS_baseUrl=http://localhost npm run cypress:run $JS_REDIRECT"
JS_REDIRECT=">/apps/whyis/test-results/js/test.out 2>/apps/whyis/test-results/js/test.err"
docker run $WHYIS_DEMO_IMAGE bash -c "mkdir -p test-results/js && curl -sL https://deb.nodesource.com/setup_12.x | bash - $JS_REDIRECT && apt-get install -y nodejs xvfb libgtk-3-dev libnotify-dev libgconf-2-4 libnss3 libxss1 libasound2 $JS_REDIRECT && cd tests/integration && npm install $JS_REDIRECT && CYPRESS_baseUrl=http://localhost npm run cypress:run-ci $JS_REDIRECT; tar cf test-results-js.tar test-results/js && cat test-results-js.tar" >test-results-js.tar
tar xf test-results-js.tar
cat test-results/js/test.out
if [ "$(grep -c 'failure ' test-results/js/results.xml)" -ge 1 ]; then
    echo "Integration test results.xml has failures, exiting abnormally"
    exit 1
fi

echo "Exiting normally"
exit 0
