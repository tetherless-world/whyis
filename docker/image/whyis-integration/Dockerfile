# For running CI purposes
FROM cypress/included:3.8.3

COPY docker/image/whyis-integration/docker-entrypoint.sh /
COPY docker/image/whyis-integration/cypress.json /integration/
COPY tests/integration/cypress /integration/cypress
WORKDIR /integration

ENTRYPOINT ["bash"]
