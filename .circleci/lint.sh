#!/bin/bash

mkdir -p lint-results/py

cd ..
pylint whyis &>whyis/lint-results/py/pylint.txt
