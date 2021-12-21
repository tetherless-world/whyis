#!/bin/bash

mkdir -p lint-results/js

cd whyis/static
npm run lint -- js/whyis.js >>../../lint-results/js/eslint.txt 2>/dev/null
npm run lint -- js/whyis_vue/** >>../../lint-results/js/eslint.txt 2>/dev/null

exit 0
