#!/bin/bash
mkdir -p test-results/py

docker run $1 bash -c "python3 manage.py test --ci &>/dev/null && cat test-results/py/results.xml" >test-results/py/results.xml

cat test-results/py/results.xml

if [ "$(grep -c "failure "test-results/py/results.xml)" -ge 1 ]; then
    exit 1
else
    exit 0
fi
