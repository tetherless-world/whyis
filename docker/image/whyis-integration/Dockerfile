# For running CI purposes
FROM cypress/included:3.2.0

COPY docker/image/whyis-integration/docker-entrypoint.sh /
COPY tests/integration/ /integration/
WORKDIR /integration

ENTRYPOINT bash
