#!/bin/bash

mkdir -p lint-results/py

flake8 . &>lint-results/py/flake8.txt

cd ..
pylint --rcfile whyis/.pylintrc whyis &>whyis/lint-results/py/pylint.txt

exit 0