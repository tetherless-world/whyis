#!/bin/bash
mkdir -p test-results/py

docker run $1 bash -c "python3 manage.py test --ci &>/dev/null && tar cf test-results-py.tar test-results/py && cat test-results-py.tar" >test-results-py.tar

tar xf test-results-py.tar

cat test-results/py/results.xml

if [ "$(grep -c "failure "test-results/py/results.xml)" -ge 1 ]; then
    exit 1
else
    exit 0
fi
