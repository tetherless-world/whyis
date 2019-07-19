#!/bin/bash

mkdir -p lint-results/py

cd ..
pylint --rcfile whyis/.pylintrc whyis &>whyis/lint-results/py/pylint.txt
