#!/bin/bash

mkdir -p lint-results/js

cd static
npm run lint &>../lint-results/js/eslint.txt

exit 0
