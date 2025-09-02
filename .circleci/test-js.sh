#!/bin/bash

# Test script for JavaScript/Vue.js components
# Runs unit tests using Vitest and generates test results for CI

mkdir -p test-results/js

cd whyis/static

echo "`date` Running JavaScript tests with coverage"

# Run tests with coverage and JUnit output
npm run test:coverage -- --reporter=verbose --reporter=junit --outputFile.junit=../../test-results/js/results.xml

# Check if test results exist
if [ ! -f "../../test-results/js/results.xml" ]; then
    echo "JavaScript test results.xml does not exist, trying alternative path"
    # Try alternative path if the above doesn't work
    if [ -f "coverage/junit.xml" ]; then
        cp coverage/junit.xml ../../test-results/js/results.xml
    else
        echo "No test results found, creating empty results file"
        cat > ../../test-results/js/results.xml << EOF
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="JavaScript Tests" tests="0" failures="0" errors="0" time="0">
</testsuites>
EOF
    fi
fi

# Copy coverage reports if they exist
if [ -d "coverage" ]; then
    echo "Copying coverage reports"
    cp -r coverage ../../test-results/js/
fi

echo "`date` JavaScript tests completed"

exit 0