# For running CI purposes
FROM cypress/included:3.2.0

COPY tests/integration/ /integration/
WORKDIR /integration
# RUN npm install -g wait-on

ENTRYPOINT curl --retry 10 --retry-connrefused http://whyis > /dev/null && CYPRESS_baseUrl=http://whyis cypress run --spec cypress/integration/whyis/**/*; tar cf test-results-js.tar results
