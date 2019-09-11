# For running CI purposes
FROM cypress/included:3.2.0

COPY tests/integration/ /integration/
WORKDIR /integration
RUN npm install -g wait-on

ENTRYPOINT npx wait-on -t 150000 http://localhost && CYPRESS_baseUrl=http://localhost cypress run --spec cypress/integration/whyis/**/*; tar cf test-results-js.tar results
