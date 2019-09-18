# For running CI purposes
FROM cypress/included:3.2.0

COPY docker/image/whyis-integration/docker-entrypoint.sh /
COPY docker/image/whyis-integration/cypress.json /integration/
COPY tests/integration/cypress /integration/cypress
WORKDIR /integration

ENTRYPOINT ["bash"]
