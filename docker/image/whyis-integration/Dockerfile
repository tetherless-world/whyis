# For running CI purposes
FROM cypress/included:3.2.0

COPY tests/integration/ /integration/
WORKDIR /integration
RUN npm install --only=dev
